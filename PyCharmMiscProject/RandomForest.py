import pandas as pd
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
from skopt import BayesSearchCV
from sklearn.model_selection import TimeSeriesSplit
import matplotlib.pyplot as plt


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
raw_data["dominant_win"] = ((raw_data["team_goals"] - raw_data["opponent_goals"]) >= 2).astype(int)
raw_data["dominant_win_ratio"] = (
    raw_data.groupby("team")["dominant_win"].transform(lambda x: x.rolling(5, closed="left", min_periods=5).mean())
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

predictors = ["venue_code", "opponent_code", 'h2h_win', 'team_total_win', 'opponent_total_win', 'h2h_avg_goals', 'dominant_win_ratio', 'clean_sheet_ratio']

def rolling_averages(group, cols, newcols):
    group = group.sort_values("date")
    rolling_stats = group[cols].rolling(3, closed="left", min_periods=3).mean()
    group[newcols] = rolling_stats.values
    return group

cols = ["possession_diff", "goal_difference", "total_shots_difference",
        "shots_on_target_difference", "xG_difference", "passing_difference"]

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

matches_rolling = matches_rolling.dropna(subset=predictors + teamnewcols + opponentnewcols + ["target"])

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

numerical_features = teamnewcols + opponentnewcols
scaler = StandardScaler()
X_train.loc[:, numerical_features] = scaler.fit_transform(X_train[numerical_features])
X_test.loc[:, numerical_features] = scaler.transform(X_test[numerical_features])


rf = RandomForestClassifier(random_state=1, class_weight='balanced')


param_grid_rf = {
    'n_estimators': (50, 75),
    'max_depth': (5, 20),
    'min_samples_split': (4, 40),
    'min_samples_leaf': (2, 20),
    'max_features': ['sqrt', 'log2', None],
    'bootstrap': [True, False]
}


tscv = TimeSeriesSplit(n_splits=5)
bayes_search_rf = BayesSearchCV(
    estimator=rf,
    search_spaces=param_grid_rf,
    n_iter=20,
    cv=tscv,
    random_state=1,
    verbose=1,
    n_jobs=-1
)


bayes_search_rf.fit(X_train, y_train)
best_rf = bayes_search_rf.best_estimator_

opt_results = pd.DataFrame(bayes_search_rf.cv_results_)
opt_results["best_score_so_far"] = opt_results["mean_test_score"].cummax()
plt.plot(opt_results.index, opt_results["best_score_so_far"], marker="o", linestyle="-", color="b")
plt.xlabel("Iteration")
plt.ylabel("Validation Score")
plt.title("Bayesian Optimization Progress For Random Forest")
plt.grid(True)
plt.show()

feature_importance = pd.DataFrame({
    'Feature': X_train.columns,
    'Importance': best_rf.feature_importances_
}).sort_values(by="Importance", ascending=False)

plt.bar(feature_importance['Feature'], feature_importance['Importance'])
plt.ylabel('Importance')
plt.xlabel('Feature')
plt.title('Feature Importance (Random Forest)')
plt.xticks(rotation=90, fontsize=10)
plt.tight_layout()
plt.show()


y_pred_rf_proba = best_rf.predict_proba(X_test)[:, 1]
threshold = 0.49
y_pred_rf = (y_pred_rf_proba > threshold).astype(int)


y_train_pred_rf = best_rf.predict(X_train)
print("\nTrain Performance:")
print(f"Accuracy: {accuracy_score(y_train, y_train_pred_rf):.4f}")
print(f"Precision: {precision_score(y_train, y_train_pred_rf, average='weighted'):.4f}")
print(f"Recall: {recall_score(y_train, y_train_pred_rf, average='weighted'):.4f}")
print(f"F1-score: {f1_score(y_train, y_train_pred_rf, average='weighted'):.4f}")


print("\nTest Performance:")
print(f"Accuracy: {accuracy_score(y_test, y_pred_rf):.4f}")
print(f"Precision: {precision_score(y_test, y_pred_rf, average='weighted'):.4f}")
print(f"Recall: {recall_score(y_test, y_pred_rf, average='weighted'):.4f}")
print(f"F1-score: {f1_score(y_test, y_pred_rf, average='weighted'):.4f}")


predictions_df_rf = pd.DataFrame({'actual': y_test, 'predicted_rf': y_pred_rf})
predictions_df_rf.to_csv("/Users/ifajkhan/Downloads/optimized_predictions_rf.csv", index=False)

print("\nClassification Report For Random Forest:")
print(classification_report(y_test, y_pred_rf))


future_matches = raw_data[raw_data["match_result"].isna()]
latest_rolling_avgs = matches_rolling.groupby("team").last()[teamnewcols + opponentnewcols].reset_index()
future_matches = future_matches.merge(latest_rolling_avgs, on="team", how="left")
X_future = future_matches[predictors + teamnewcols + opponentnewcols]
X_future.loc[:, numerical_features] = scaler.transform(X_future[numerical_features])
future_matches["predicted_target"] = best_rf.predict(X_future)
future_matches.to_csv("/Users/ifajkhan/Downloads/future_predictions_rf.csv", index=False)


from sklearn.metrics import confusion_matrix


cm = confusion_matrix(y_test, y_pred_rf)


plt.figure(figsize=(6, 4))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=["Loss or Draw (0)", "Win (1)"], yticklabels=["Loss or Draw (0)", "Win (1)"])
plt.xlabel("Predicted Label")
plt.ylabel("True Label")
plt.title("Confusion Matrix For Random Forest")
plt.show()