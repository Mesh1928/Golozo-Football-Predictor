import pandas as pd
from xgboost import XGBClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
from skopt import BayesSearchCV
from sklearn.model_selection import TimeSeriesSplit
import matplotlib.pyplot as plt
import seaborn as sns


raw_data = pd.read_csv('/Users/ifajkhan/Documents/FinalDatabase.csv')


raw_data = raw_data.sort_values("date")


raw_data['h2h_win'] = raw_data.groupby(['team', 'opponent'])['target'].transform(
    lambda x: (x == 1).astype(int).rolling(3, closed="left", min_periods=3).sum()
)
raw_data["team_total_win"] = raw_data.groupby("team")["target"].transform(
    lambda x: (x == 1).astype(int).rolling(5, closed="left", min_periods=5).sum()
)

raw_data["opponent_total_win"] = raw_data.groupby("opponent").apply(
    lambda x: (x["opponent_goals"] > x["team_goals"]).astype(int).rolling(5, closed="left", min_periods=5).sum()
).reset_index(level=0, drop=True)

raw_data['h2h_avg_goals'] = raw_data.groupby(['team', 'opponent'])['team_goals'].transform(
    lambda x: x.rolling(3, min_periods=3, closed="left").mean()
)

raw_data["dominant_win"] = ((raw_data["team_goals"] -raw_data["opponent_goals"]) >= 2).astype(int)

raw_data["dominant_win_ratio"] = (
    raw_data.groupby("team")["dominant_win"].transform(lambda x: x.rolling(5, closed= "left", min_periods=5).mean())
)



raw_data['possession_diff'] = raw_data['home_possession'] - raw_data['away_possession']
raw_data["goal_difference"] = raw_data["team_goals"] - raw_data["opponent_goals"]
raw_data["total_shots_difference"] = raw_data["total_team_shots"] - raw_data["total_opponent_shots"]
raw_data["shots_on_target_difference"] = raw_data["team_shots_on_target"] - raw_data["opponent_shots_on_target"]
raw_data["xG_difference"] = raw_data["team_xG"] - raw_data["opponent_xG"]
raw_data["passing_difference"] = raw_data["team_passing"] - raw_data["opponent_passing"]
raw_data["clean_sheet"] = (raw_data["opponent_goals"] == 0).astype(int)
raw_data["clean_sheet_ratio"] = raw_data.groupby("team")["clean_sheet"].transform(
    lambda x: x.rolling(5, closed="left", min_periods=5).mean()
)

print(raw_data.columns)
print(raw_data["target"].value_counts())


predictors = ["venue_code", "opponent_code", 'h2h_win', 'team_total_win', 'opponent_total_win','h2h_avg_goals', 'dominant_win_ratio', 'clean_sheet_ratio']


def rolling_averages(group, cols, newcols):
    group = group.sort_values("date")
    rolling_stats = group[cols].rolling(3, closed="left", min_periods=3).mean()
    group[newcols] = rolling_stats.values
    return group


cols = [ "possession_diff", "goal_difference", "total_shots_difference",
         "shots_on_target_difference", "xG_difference", "passing_difference"
]

teamnewcols = [f"{c}_ra_teams" for c in cols]


matches_rolling = (
    raw_data.groupby("team", group_keys=False)
    .apply(lambda x: rolling_averages(x, cols, teamnewcols))
    .reset_index(drop=True)
)

opponentnewcols = [f"{c}_ra_opponent" for c in cols]

matches_rolling = (
    matches_rolling.groupby("opponent", group_keys=False)
    .apply(lambda x: rolling_averages(x, cols, opponentnewcols))
    .reset_index(drop=True)
)

print(matches_rolling.columns)


matches_rolling = matches_rolling.dropna(subset=predictors + teamnewcols + opponentnewcols +  ["target"])

print(matches_rolling.columns)

matches_rolling.to_csv("/Users/ifajkhan/Downloads/zz.csv", index=False)
print(matches_rolling.shape)
correlation_matrix = matches_rolling[predictors + teamnewcols + opponentnewcols].corr()
plt.figure(figsize=(12, 8))
sns.heatmap(correlation_matrix, annot=True, fmt=".2f", cmap="coolwarm", linewidths=0.5)
plt.title("Feature Correlation Heatmap")
plt.xticks(rotation=90)
plt.yticks(rotation=0)
plt.tight_layout()
plt.show()


train = matches_rolling[matches_rolling["date"] < '2024-01-18']
test = matches_rolling[matches_rolling["date"] >= '2024-01-18']
X_train, y_train = train[predictors + teamnewcols + opponentnewcols], train["target"]
X_test, y_test = test[predictors + teamnewcols + opponentnewcols], test["target"]
print(y_train.value_counts(), y_test.value_counts())

numerical_features = teamnewcols + opponentnewcols
scaler = StandardScaler()
X_train.loc[:, numerical_features] = scaler.fit_transform(X_train[numerical_features])
X_test.loc[:, numerical_features] = scaler.transform(X_test[numerical_features])



num_negatives = y_train.value_counts()[0]
num_positives = y_train.value_counts()[1]
scale_pos_weight = num_negatives / num_positives



xgb = XGBClassifier(
    random_state=1,
    objective='binary:logistic',
    eval_metric="logloss",
    scale_pos_weight=scale_pos_weight,

)


param_grid = {
    'n_estimators': (200, 500),
    'learning_rate': (0.01, 0.3, 'log-uniform'),
    'max_depth': (3, 10),
    'subsample': (0.6, 1.0),
    'colsample_bytree': (0.4, 1.0),
    'gamma': (0.0, 3.0),
    'min_child_weight': (5,20),
    'lambda': (0, 10.0),
    'alpha': (1.0, 10.0)
}

tscv = TimeSeriesSplit(n_splits=5)
bayes_search = BayesSearchCV(
    estimator=xgb,
    search_spaces=param_grid,
    n_iter=20,
    cv=tscv,
    random_state=1,
    verbose=1,
    n_jobs=-1
)


bayes_search.fit(X_train, y_train)
best_model = bayes_search.best_estimator_


opt_results = pd.DataFrame(bayes_search.cv_results_)
opt_results["best_score_so_far"] = opt_results["mean_test_score"].cummax()
plt.plot(opt_results.index, opt_results["best_score_so_far"], marker="o", linestyle="-", color="b")
plt.xlabel("Iteration")
plt.ylabel("Validation Score")
plt.title("Bayesian Optimization Progress For XGBoost")
plt.grid(True)
plt.show()

feature_importance = pd.DataFrame({
    'Feature': X_train.columns,
    'Importance': best_model.feature_importances_
}).sort_values(by="Importance", ascending=False)
print(feature_importance)

plt.bar(feature_importance['Feature'], feature_importance['Importance'])
plt.ylabel('Importance')
plt.xlabel('Feature')
plt.title('Feature Importance (XGBoost)')
plt.xticks(rotation=90, fontsize=10)
plt.tight_layout()
plt.show()


y_pred_proba = best_model.predict_proba(X_test)[:, 1]
threshold = 0.5
y_pred = (y_pred_proba > threshold).astype(int)


y_train_pred = best_model.predict(X_train)


print(f"Train Accuracy: {accuracy_score(y_train, y_train_pred):.4f}")
print(f"Train Precision: {precision_score(y_train, y_train_pred, average='weighted'):.4f}")
print(f"Train Recall: {recall_score(y_train, y_train_pred, average='weighted'):.4f}")
print(f"Train F1-score: {f1_score(y_train, y_train_pred, average='weighted'):.4f}")


print(f"Test Accuracy: {accuracy_score(y_test, y_pred):.4f}")
print(f"Test Precision: {precision_score(y_test, y_pred, average='weighted'):.4f}")
print(f"Test Recall: {recall_score(y_test, y_pred, average='weighted'):.4f}")
print(f"Test F1-score: {f1_score(y_test, y_pred, average='weighted'):.4f}")



predictions_df = pd.DataFrame({'actual': y_test, 'predicted': y_pred})
predictions_df.to_csv("/Users/ifajkhan/Downloads/optimized_predictions.csv", index=False)



print("\nClassification Report For XGBoost:")
print(classification_report(y_test, y_pred))


future_matches = raw_data[raw_data["match_result"].isna()]
latest_rolling_avgs = (matches_rolling.groupby("team").last()[teamnewcols + opponentnewcols].
                       reset_index())
future_matches = future_matches.merge(latest_rolling_avgs, on="team", how="left")
X_future = future_matches[predictors + teamnewcols + opponentnewcols]
X_future.loc[:, numerical_features] = scaler.transform(X_future[numerical_features])
future_matches["predicted_target"] = best_model.predict(X_future)
future_matches.to_csv("/Users/ifajkhan/Downloads/future_predictions_withXGBV2.csv", index=False)

from sklearn.metrics import confusion_matrix


cm = confusion_matrix(y_test, y_pred)


plt.figure(figsize=(6, 4))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=["Loss or Draw (0)", "Win (1)"], yticklabels=["Loss or Draw (0)", "Win (1)"])
plt.xlabel("Predicted Label")
plt.ylabel("True Label")
plt.title("Confusion Matrix For XGBoost")
plt.show()

