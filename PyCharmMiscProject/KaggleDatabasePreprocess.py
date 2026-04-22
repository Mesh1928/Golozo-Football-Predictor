import pandas as pd

db = pd.read_csv('/Users/ifajkhan/Downloads/KaggleDB.csv')

db = db.sort_values("date")
columns_to_remove = [
    'game_id', 'round', 'home_club_id', 'away_club_id',
    'home_club_position', 'away_club_position', 'home_club_manager_name',
    'away_club_manager_name', 'stadium', 'attendance', 'referee', 'url',
    'aggregate', 'competition_type', 'home_club_formation', 'away_club_formation'
]


db = db.drop(columns=columns_to_remove, errors='ignore')
db = db[db["competition_id"] == "GB1"]

db = db.drop(columns='competition_id', errors='ignore')

db["date"] = pd.to_datetime(db["date"])
db = db[db["date"] >= "2017-08-11"]



db = db.rename(columns={
    "home_club_goals": "team_goals",
    "away_club_goals": "opponent_goals",
    "home_club_name": "team",
    "away_club_name": "opponent"
})


reverse_db = db.copy()
reverse_db["team"], reverse_db["opponent"] = db["opponent"], db["team"]
reverse_db["team_goals"], reverse_db["opponent_goals"] = db["opponent_goals"], db["team_goals"]
db["venue_code"] = 1
reverse_db["venue_code"] = 0

db = pd.concat([db, reverse_db], ignore_index=True)

def determine_result(team_goals, opponent_goals):
    if team_goals is None or opponent_goals is None:
        return "N/A"
    elif team_goals > opponent_goals:
        return "W"
    elif team_goals < opponent_goals:
        return "L"
    else:
        return "D"

def target(team_goals, opponent_goals):
    if team_goals is None or opponent_goals is None:
        return "N/A"
    elif team_goals > opponent_goals:
        return 1
    else:

        return 0


db["match_result"] = db.apply(lambda row: determine_result(row["team_goals"], row["opponent_goals"]), axis=1)
db["target"] = db.apply(lambda row: target(row["team_goals"], row["opponent_goals"]), axis=1)


team_name_mapping = {
    "Arsenal Football Club": "Arsenal",
    "Watford FC": "Watford",
    "Crystal Palace Football Club": "Crystal Palace",
    "West Bromwich Albion": "West Brom",
    "Southampton Football Club": "Southampton",
    "Brighton and Hove Albion Football Club": "Brighton",
    "Chelsea Football Club": "Chelsea",
    "Everton Football Club": "Everton",
    "Manchester United Football Club": "Manchester Utd",
    "Newcastle United Football Club": "Newcastle Utd",
    "Liverpool Football Club": "Liverpool",
    "Swansea City": "Swansea City",
    "Stoke City": "Stoke City",
    "Burnley FC": "Burnley",
    "Leicester City Football Club": "Leicester City",
    "Association Football Club Bournemouth": "Bournemouth",
    "Huddersfield Town": "Huddersfield",
    "Tottenham Hotspur Football Club": "Tottenham",
    "Manchester City Football Club": "Manchester City",
    "West Ham United Football Club": "West Ham",
    "Wolverhampton Wanderers Football Club": "Wolves",
    "Fulham Football Club": "Fulham",
    "Cardiff City": "Cardiff City",
    "Norwich City": "Norwich City",
    "Aston Villa Football Club": "Aston Villa",
    "Sheffield United": "Sheffield Utd",
    "Leeds United": "Leeds United",
    "Brentford Football Club": "Brentford",
    "Nottingham Forest Football Club": "Nott'ham Forest",
    "Luton Town": "Luton Town",
    "Ipswich Town Football Club": "Ipswich Town"
}

db["team"] = db["team"].replace(team_name_mapping)
db["opponent"] = db["opponent"].replace(team_name_mapping)
db["daycode"] = db["date"].dt.weekday
db["opponent_code"] = db["opponent"].astype("category").cat.codes


db.to_csv('/Users/ifajkhan/Documents/NoFeatureDatabase.csv', index = False)

print(db['team'].unique())






