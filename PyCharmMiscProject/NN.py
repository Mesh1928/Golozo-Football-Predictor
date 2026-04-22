import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow import keras
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
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

raw_data["dominant_win"] = ((raw_data["team_goals"] - raw_data["opponent_goals"]) >= 2).astype(int)

raw_data["dominant_win_ratio"] = raw_data.groupby("team")["dominant_win"].transform(
    lambda x: x.rolling(5, closed="left", min_periods=5).mean()
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


predictors = ["venue_code", "opponent_code", 'h2h_win', 'team_total_win', 'opponent_total_win',
              'h2h_avg_goals', 'dominant_win_ratio', 'clean_sheet_ratio']


def rolling_averages(group, cols, newcols):
    group = group.sort_values("date")
    rolling_stats = group[cols].rolling(3, closed="left", min_periods=3).mean()
    group[newcols] = rolling_stats.values
    return group


cols = ["possession_diff", "goal_difference", "total_shots_difference",
        "shots_on_target_difference", "xG_difference", "passing_difference"]

teamnewcols = [f"{c}_ra_teams" for c in cols]

matches_rolling = raw_data.groupby("team", group_keys=False).apply(
    lambda x: rolling_averages(x, cols, teamnewcols)
).reset_index(drop=True)

opponentnewcols = [f"{c}_ra_opponent" for c in cols]

matches_rolling = matches_rolling.groupby("opponent", group_keys=False).apply(
    lambda x: rolling_averages(x, cols, opponentnewcols)
).reset_index(drop=True)


matches_rolling = matches_rolling.dropna(subset=predictors + teamnewcols + opponentnewcols + ["target"])


train = matches_rolling[matches_rolling["date"] < '2024-01-18']
test = matches_rolling[matches_rolling["date"] >= '2024-01-18']
X_train, y_train = train[predictors + teamnewcols + opponentnewcols], train["target"]
X_test, y_test = test[predictors + teamnewcols + opponentnewcols], test["target"]


numerical_features = teamnewcols + opponentnewcols
scaler = StandardScaler()
X_train[numerical_features] = scaler.fit_transform(X_train[numerical_features])
X_test[numerical_features] = scaler.transform(X_test[numerical_features])



def build_nn_model(input_dim):
    model = keras.Sequential([
        keras.layers.Dense(128, activation='relu', input_shape=(input_dim,)),
        keras.layers.BatchNormalization(),
        keras.layers.Dropout(0.2),
        keras.layers.Dense(64, activation='relu'),
        keras.layers.BatchNormalization(),
        keras.layers.Dropout(0.3),
        keras.layers.Dense(32, activation='relu'),
        keras.layers.BatchNormalization(),
        keras.layers.Dense(1, activation='sigmoid')
    ])

    model.compile(optimizer=keras.optimizers.Adam(learning_rate=0.001),
                  loss='binary_crossentropy',
                  metrics=['accuracy'])

    return model



nn_model = build_nn_model(X_train.shape[1])
early_stopping = keras.callbacks.EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

history = nn_model.fit(
    X_train, y_train,
    validation_data=(X_test, y_test),
    epochs=50,
    batch_size=32,
    callbacks=[early_stopping],
    verbose=1
)


y_pred_proba = nn_model.predict(X_test).flatten()
threshold = 0.4
y_pred = (y_pred_proba > threshold).astype(int)

y_train_pred_proba = nn_model.predict(X_train).flatten()
y_train_pred = (y_train_pred_proba > threshold).astype(int)


print(f"Train Accuracy: {accuracy_score(y_train, y_train_pred):.4f}")
print(f"Train Precision: {precision_score(y_train, y_train_pred, average='weighted'):.4f}")
print(f"Train Recall: {recall_score(y_train, y_train_pred, average='weighted'):.4f}")
print(f"Train F1-score: {f1_score(y_train, y_train_pred, average='weighted'):.4f}")

print(f"Test Accuracy: {accuracy_score(y_test, y_pred):.4f}")
print(f"Test Precision: {precision_score(y_test, y_pred, average='weighted'):.4f}")
print(f"Test Recall: {recall_score(y_test, y_pred, average='weighted'):.4f}")
print(f"Test F1-score: {f1_score(y_test, y_pred, average='weighted'):.4f}")

print("\nClassification Report For MLP:")
print(classification_report(y_test, y_pred))


predictions_df = pd.DataFrame({'actual': y_test, 'predicted': y_pred})
predictions_df.to_csv("/Users/ifajkhan/Downloads/nn_predictions.csv", index=False)

nn_model.save("/Users/ifajkhan/Downloads/nn_model.h5")

from sklearn.metrics import confusion_matrix


cm = confusion_matrix(y_test, y_pred)


plt.figure(figsize=(6, 4))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=["Loss or Draw (0)", "Win (1)"], yticklabels=["Loss or Draw (0)", "Win (1)"])
plt.xlabel("Predicted Label")
plt.ylabel("True Label")
plt.title("Confusion Matrix For MLP")
plt.show()