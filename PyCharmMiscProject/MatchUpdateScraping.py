from datetime import datetime
import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import re


options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=options)


url = "https://fbref.com/en/comps/9/2024-2025/schedule/2024-2025-Premier-League-Scores-and-Fixtures"
driver.get(url)

time.sleep(5)
html = driver.page_source
try:
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "sched_2024-2025_9_1"))
    )
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", {"id": "sched_2024-2025_9_1"})

    if not table:
        driver.quit()
        exit()


except Exception as e:
    print("Error")
    driver.quit()
    exit()

cutoff_date = datetime(2025, 3, 16)


html = driver.page_source
soup = BeautifulSoup(html, "html.parser")
table = soup.find("table", {"id": "sched_2024-2025_9_1"})

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
matches = table.find("tbody").find_all("tr")

new_matches = []

for match in matches:
    columns = match.find_all("td")
    if len(columns) >= 8:
        date = columns[1].text.strip()
        home_team = columns[3].text.strip()
        home_xg = columns[4].text.strip()
        away_xg = columns[6].text.strip()
        away_team = columns[7].text.strip()
        score = columns[5].text.strip()

        report_column = match.find("td", {"data-stat": "match_report"})
        if report_column:
            link_tag = report_column.find("a")
            if link_tag and 'href' in link_tag.attrs:
                match_report_link = "https://fbref.com" + link_tag["href"]

            else:
                print("Match Report column exists, but no link found")

        else:
            print("N/A")

        team_total_shots = None
        opponent_total_shots = None
        team_passing = None
        opponent_passing = None
        home_possession = None
        away_possession = None
        team_total_shots = None
        opponent_total_shots = None
        team_shots_on_target = None
        opponent_shots_on_target = None


        date = date.replace(r'^[A-Za-z]+, ', '')
        date = pd.to_datetime(date, errors='coerce')


        if date < cutoff_date:
            continue

        home_xg = float(home_xg) if home_xg.replace('.', '', 1).isdigit() else None
        away_xg = float(away_xg) if away_xg.replace('.', '', 1).isdigit() else None


        if score and ('-' in score or '–' in score):
            score = score.replace('–', '-')
            try:
                team_goals, opponent_goals = score.split('-')
                team_goals = int(team_goals.strip())
                opponent_goals = int(opponent_goals.strip())
            except ValueError:
                team_goals = opponent_goals = None
        else:
            team_goals = opponent_goals = None

        if match_report_link:
            driver.get(match_report_link)
            time.sleep(6)
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "team_stats"))
                )
                page_source = driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')
                team_stats = soup.find("div", {"id": "team_stats"})
                percentage_values = team_stats.find_all("strong")

                if len(percentage_values) >= 2:
                    home_possession = percentage_values[0].text.strip().replace('%', '')
                    away_possession = percentage_values[1].text.strip().replace('%', '')
                    home_possession = float(
                        home_possession) / 100 if home_possession.isdigit() or '.' in home_possession else None
                    away_possession = float(
                        away_possession) / 100 if away_possession.isdigit() or '.' in away_possession else None
                    team_passing = percentage_values[2].text.strip().replace('%', '')
                    opponent_passing = percentage_values[3].text.strip().replace('%', '')
                    team_passing = float(
                        team_passing) / 100 if team_passing.isdigit() or '.' in team_passing else None
                    opponent_passing = float(
                        opponent_passing) / 100 if opponent_passing.isdigit() or '.' in opponent_passing else None
                    print(f"Home possession: {home_possession}")
                    print(f"Away possession: {away_possession}")
                    print(f"Team passing: {team_passing}")
                    print(f"Opponent passing: {opponent_passing}")
                if team_stats:
                    shots_on_target_row = team_stats.find_all("tr")
                    for i in range(len(shots_on_target_row)):
                        header = shots_on_target_row[i].find("th")
                        if header and "Shots on Target" in header.get_text():
                            shots_data_row = shots_on_target_row[i + 1].find_all("td")
                            if len(shots_data_row) == 2:
                                home_shots_text = shots_data_row[0].get_text(strip=True)
                                away_shots_text = shots_data_row[1].get_text(strip=True)

                                print(f"Raw home shots text: {home_shots_text}")
                                print(f"Raw away shots text: {away_shots_text}")

                                home_shots = home_shots_text.split(" of ")[0]
                                total_home_shots = home_shots_text.split(" of ")[1].split()[0]

                                away_shots_match = re.search(r'(\d+) of (\d+)', away_shots_text)
                                away_shots = away_shots_match.group(1) if away_shots_match else None
                                total_away_shots = away_shots_match.group(2) if away_shots_match else None

                                team_total_shots = int(total_home_shots) if total_home_shots.isdigit() else None
                                opponent_total_shots = int(total_away_shots) if total_away_shots.isdigit() else None

                                team_shots_on_target = int(home_shots) if home_shots.isdigit() else None
                                opponent_shots_on_target = int(away_shots) if away_shots.isdigit() else None

                            print(f"Home shots on target: {team_shots_on_target}")
                            print(f"Away shots on target: {opponent_shots_on_target}")
                            print(f"Total Team shots: {team_total_shots}")
                            print(f"Total Opponent shots: {opponent_total_shots}")


            except Exception as e:
                print(f"Possession scraping failed for {match_report_link}: {e}")
                home_possession = None
                away_possession = None



        match_entry = {
            "date": date,
            "team": home_team,
            "opponent": away_team,
            "team_xG": home_xg,
            "opponent_xG": away_xg,
            "team_goals": team_goals,
            "opponent_goals": opponent_goals,
            "venue_code" : 1,
            "season": 2024,
            "match_result": determine_result(team_goals, opponent_goals),
            "target": target(team_goals, opponent_goals),
            "home_possession": home_possession,
            "away_possession": away_possession,
            "team_passing": team_passing,
            "opponent_passing": opponent_passing,
            "team_shots_on_target": team_shots_on_target,
            "opponent_shots_on_target": opponent_shots_on_target,
            "total_team_shots": team_total_shots,
            "total_opponent_shots": opponent_total_shots,
        }

        reverse_entry = {
            "date": date,
            "team": away_team,
            "opponent": home_team,
            "team_xG": away_xg,
            "opponent_xG": home_xg,
            "team_goals": opponent_goals,
            "opponent_goals": team_goals,
            "venue_code": 0,
            "season": 2024,
            "match_result": determine_result(opponent_goals, team_goals),
            "target": target(opponent_goals, team_goals),
            "home_possession": away_possession,
            "away_possession": home_possession,
            "team_passing": opponent_passing,
            "opponent_passing": team_passing,
            "team_shots_on_target": opponent_shots_on_target,
            "opponent_shots_on_target": team_shots_on_target,
            "total_team_shots": opponent_total_shots,
            "total_opponent_shots": team_total_shots,
        }

        new_matches.append(match_entry)
        new_matches.append(reverse_entry)


driver.quit()


matches_df = pd.DataFrame(new_matches)


matches_df['team_goals'] = pd.to_numeric(matches_df['team_goals'], errors='coerce')
matches_df['opponent_goals'] = pd.to_numeric(matches_df['opponent_goals'], errors='coerce')

current_df = pd.read_csv('/Users/ifajkhan/Documents/FeatureDatabase.csv')

opponent_code_map = current_df.set_index("opponent")["opponent_code"].to_dict()
matches_df["opponent_code"] = matches_df["opponent"].map(opponent_code_map)

current_df["date"] = pd.to_datetime(current_df["date"])


current_df['team_goals'] = pd.to_numeric(current_df['team_goals'], errors='coerce')
current_df['opponent_goals'] = pd.to_numeric(current_df['opponent_goals'], errors='coerce')

print(current_df.dtypes)


current_df_cleaned = current_df.dropna(subset=["team_goals", "opponent_goals"])
matches_df['daycode'] = matches_df['date'].dt.weekday
current_df_cleaned['daycode'] = current_df_cleaned['date'].dt.weekday

merged = current_df_cleaned.merge(
    matches_df,
    on=["date", "team", "opponent", "team_goals",
        "opponent_goals", "team_xG", "opponent_xG", "season", "venue_code", "match_result",
        "target", "opponent_code", "daycode", 'home_possession', 'away_possession', 'opponent_shots_on_target',
        'team_shots_on_target', 'team_passing','opponent_passing','total_team_shots', 'total_opponent_shots'],
    how="right",
    indicator=True,
    suffixes=('_existing', '_new')
)



missing_matches = merged[merged["_merge"] == "right_only"].drop(columns=["_merge"])


database_updated = pd.concat(
    [current_df, missing_matches],
    ignore_index=True
).drop_duplicates(subset=["date", "team", "opponent",
                          "team_goals", "opponent_goals",
                          "team_xG", "opponent_xG", "season",
                          "venue_code", "match_result", "target",
                          "opponent_code", "daycode", 'home_possession',
                          'away_possession', 'opponent_shots_on_target',
                          'team_shots_on_target','team_passing','opponent_passing',
                          'total_team_shots','total_opponent_shots'], keep="last")




database_updated['team_goals'] = database_updated['team_goals'].fillna(np.nan)
database_updated['opponent_goals'] = database_updated['opponent_goals'].fillna(np.nan)
database_updated['daycode'] = database_updated['daycode'].fillna(database_updated['date'].dt.weekday)


database_updated = database_updated.dropna(subset=['date', 'team', 'opponent'])
database_updated = database_updated.sort_values(by="date", ascending=True)

column_order = [
    'season', 'date', 'team', 'team_goals','total_team_shots','team_shots_on_target','team_xG','team_passing','home_possession', 'opponent', 'opponent_goals','total_opponent_shots','opponent_shots_on_target', 'opponent_xG', 'opponent_passing','away_possession', 'match_result', 'venue_code',
    'opponent_code', 'daycode', 'target'
]


database_updated = database_updated[column_order]

database_updated.to_csv('/Users/ifajkhan/Documents/FinalDatabase.csv', index=False)
print(database_updated.columns)



