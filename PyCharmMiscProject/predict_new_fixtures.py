import pandas as pd
from xgboost import XGBClassifier
from sklearn.preprocessing import StandardScaler
from sqlalchemy import create_engine
import traceback

try:
    raw_data = pd.read_csv(r'C:\Users\Mac 65-61\Desktop\Disso\CS3607_2211674\CS3607_2211674\FinalDatabase.csv')
    raw_data = raw_data.sort_values("date").reset_index(drop=True)
    print("Data loaded:", raw_data.shape)

    raw_data['h2h_win'] = raw_data.groupby(['team', 'opponent'])['target'].transform(
        lambda x: (x == 1).astype(int).rolling(3, closed="left", min_periods=3).sum())
    raw_data["team_total_win"] = raw_data.groupby("team")["target"].transform(
        lambda x: (x == 1).astype(int).rolling(5, closed="left", min_periods=5).sum())
    raw_data["opponent_total_win"] = raw_data.groupby("opponent").apply(
        lambda x: (x["opponent_goals"] > x["team_goals"]).astype(int).rolling(5, closed="left", min_periods=5).sum()
    ).reset_index(level=0, drop=True)
    raw_data['h2h_avg_goals'] = raw_data.groupby(['team', 'opponent'])['team_goals'].transform(
        lambda x: x.rolling(3, min_periods=3, closed="left").mean())
    raw_data["dominant_win"] = ((raw_data["team_goals"] - raw_data["opponent_goals"]) >= 2).astype(int)
    raw_data["dominant_win_ratio"] = raw_data.groupby("team")["dominant_win"].transform(
        lambda x: x.rolling(5, closed="left", min_periods=5).mean())
    raw_data['possession_diff'] = raw_data['home_possession'] - raw_data['away_possession']
    raw_data["goal_difference"] = raw_data["team_goals"] - raw_data["opponent_goals"]
    raw_data["total_shots_difference"] = raw_data["total_team_shots"] - raw_data["total_opponent_shots"]
    raw_data["shots_on_target_difference"] = raw_data["team_shots_on_target"] - raw_data["opponent_shots_on_target"]
    raw_data["xG_difference"] = raw_data["team_xG"] - raw_data["opponent_xG"]
    raw_data["passing_difference"] = raw_data["team_passing"] - raw_data["opponent_passing"]
    raw_data["clean_sheet"] = (raw_data["opponent_goals"] == 0).astype(int)
    raw_data["clean_sheet_ratio"] = raw_data.groupby("team")["clean_sheet"].transform(
        lambda x: x.rolling(5, closed="left", min_periods=5).mean())
    print("Feature engineering OK")

    predictors = ["venue_code", "opponent_code", 'h2h_win', 'team_total_win', 'opponent_total_win',
                  'h2h_avg_goals', 'dominant_win_ratio', 'clean_sheet_ratio']

    cols = ["possession_diff", "goal_difference", "total_shots_difference",
            "shots_on_target_difference", "xG_difference", "passing_difference"]
    teamnewcols = [f"{c}_ra_teams" for c in cols]
    opponentnewcols = [f"{c}_ra_opponent" for c in cols]

    def rolling_averages(group, cols, newcols):
        group = group.sort_values("date")
        rolling_stats = group[cols].rolling(3, closed="left", min_periods=3).mean()
        group[newcols] = rolling_stats.values
        return group

    matches_rolling = raw_data.groupby("team", group_keys=False).apply(
        lambda x: rolling_averages(x, cols, teamnewcols)).reset_index(drop=True)
    matches_rolling = matches_rolling.groupby("opponent", group_keys=False).apply(
        lambda x: rolling_averages(x, cols, opponentnewcols)).reset_index(drop=True)

    # Add team column back
    matches_rolling["team"] = raw_data["team"]
    matches_rolling = matches_rolling.dropna(subset=predictors + teamnewcols + opponentnewcols + ["target"])
    print("Rolling averages OK:", matches_rolling.shape)

    train = matches_rolling[matches_rolling["date"] < '2024-01-18']
    X_train, y_train = train[predictors + teamnewcols + opponentnewcols], train["target"]

    numerical_features = teamnewcols + opponentnewcols
    scaler = StandardScaler()
    X_train = X_train.copy()
    X_train.loc[:, numerical_features] = scaler.fit_transform(X_train[numerical_features])

    num_negatives = y_train.value_counts()[0]
    num_positives = y_train.value_counts()[1]
    scale_pos_weight = num_negatives / num_positives

    xgb = XGBClassifier(random_state=1, objective='binary:logistic',
                        eval_metric="logloss", scale_pos_weight=scale_pos_weight,
                        n_estimators=300, learning_rate=0.05, max_depth=6)
    xgb.fit(X_train, y_train)
    print("Model trained OK")

    new_fixtures = pd.read_csv(r'C:\Users\Mac 65-61\Desktop\Disso\CS3607_2211674\CS3607_2211674\remaining_fixtures_2026.csv')
    print("New fixtures loaded:", new_fixtures.shape)

    opponent_code_map = raw_data.set_index("opponent")["opponent_code"].to_dict()
    new_fixtures["opponent_code"] = new_fixtures["opponent"].map(opponent_code_map)

    latest_rolling_avgs = matches_rolling.sort_values("date").groupby("team").last()[teamnewcols + opponentnewcols].reset_index()
    new_fixtures = new_fixtures.merge(latest_rolling_avgs, on="team", how="left")

    for col in ['h2h_win', 'team_total_win', 'opponent_total_win', 'h2h_avg_goals', 'dominant_win_ratio', 'clean_sheet_ratio']:
        if col not in new_fixtures.columns:
            new_fixtures[col] = 0
        new_fixtures[col] = new_fixtures[col].fillna(0)

    X_future = new_fixtures[predictors + teamnewcols + opponentnewcols].fillna(0)
    X_future = X_future.copy()
    X_future.loc[:, numerical_features] = scaler.transform(X_future[numerical_features])
    new_fixtures["predicted_target"] = xgb.predict(X_future)
    print("Predictions made!")
    print(new_fixtures[["team", "opponent", "date", "predicted_target"]])

    engine = create_engine("mysql+pymysql://root:2468goku@localhost/GolozoDB")
    new_fixtures.to_sql("matches", con=engine, if_exists="append", index=False)
    print("Done! New fixtures added to database.")

except Exception as e:
    traceback.print_exc()