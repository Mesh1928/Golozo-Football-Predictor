import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import re

options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)
all_data = []


urls = [
    "https://fbref.com/en/comps/9/2017-2018/schedule/2017-2018-Premier-League-Scores-and-Fixtures",
    "https://fbref.com/en/comps/9/2018-2019/schedule/2018-2019-Premier-League-Scores-and-Fixtures",
    "https://fbref.com/en/comps/9/2019-2020/schedule/2019-2020-Premier-League-Scores-and-Fixtures",
    "https://fbref.com/en/comps/9/2020-2021/schedule/2020-2021-Premier-League-Scores-and-Fixtures",
    "https://fbref.com/en/comps/9/2021-2022/schedule/2021-2022-Premier-League-Scores-and-Fixtures",
    "https://fbref.com/en/comps/9/2022-2023/schedule/2022-2023-Premier-League-Scores-and-Fixtures",
    "https://fbref.com/en/comps/9/2023-2024/schedule/2023-2024-Premier-League-Scores-and-Fixtures",
    "https://fbref.com/en/comps/9/2024-2025/schedule/2024-2025-Premier-League-Scores-and-Fixtures"
]
for url in urls:
    driver.get(url)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "sched_2017-2018_9_1" if '2017-2018' in url else
            "sched_2018-2019_9_1" if '2018-2019' in url else
            "sched_2019-2020_9_1" if '2019-2020' in url else
            "sched_2020-2021_9_1" if '2020-2021' in url else
            "sched_2021-2022_9_1" if '2021-2022' in url else
            "sched_2022-2023_9_1" if '2022-2023' in url else
            "sched_2023-2024_9_1" if '2023-2024' in url else
            "sched_2024-2025_9_1"))
        )

    except:
        continue

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")


    season_id = "sched_2017-2018_9_1" if '2017-2018' in url else \
        "sched_2018-2019_9_1" if '2018-2019' in url else \
            "sched_2019-2020_9_1" if '2019-2020' in url else \
                "sched_2020-2021_9_1" if '2020-2021' in url else \
                    "sched_2021-2022_9_1" if '2021-2022' in url else \
                        "sched_2022-2023_9_1" if '2022-2023' in url else \
                            "sched_2023-2024_9_1" if '2023-2024' in url else \
                                "sched_2024-2025_9_1"

    table = soup.find("table", {"id": season_id})


    matches = table.find("tbody").find_all("tr")

    for match in matches:
        columns = match.find_all("td")
        if len(columns) >= 8:
            date = columns[1].text.strip()
            home_team = columns[3].text.strip()
            home_xg = columns[4].text.strip()
            away_xg = columns[6].text.strip()
            away_team = columns[7].text.strip()

            report_column = match.find("td", {"data-stat": "match_report"})
            if report_column:
                link_tag = report_column.find("a")
                if link_tag and 'href' in link_tag.attrs:
                    match_report_link = "https://fbref.com" + link_tag["href"]
                    print(f"Match report link: {match_report_link}")
                else:
                    print("Match Report column exists but no link found")
            else:
                print("Error")

            team_passing = None
            opponent_passing = None
            home_possession = None
            away_possession = None
            team_total_shots = None
            opponent_total_shots = None
            team_shots_on_target = None
            opponent_shots_on_target = None
            if match_report_link:
                driver.get(match_report_link)
                time.sleep(10)
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

            home_xg = float(home_xg) if home_xg.replace('.', '', 1).isdigit() else None
            away_xg = float(away_xg) if away_xg.replace('.', '', 1).isdigit() else None

            all_data.append({
                "date": date,
                "team": home_team,
                "team_xG": home_xg,
                "opponent": away_team,
                "opponent_xG": away_xg,
                "home_possession": home_possession,
                "away_possession": away_possession,
                "team_passing": team_passing,
                "opponent_passing": opponent_passing,
                "team_shots_on_target": team_shots_on_target,
                "opponent_shots_on_target": opponent_shots_on_target,
                "total_team_shots": team_total_shots,
                "total_opponent_shots": opponent_total_shots,
            })
            all_data.append({
                "date": date,
                "team": away_team,
                "team_xG": away_xg,
                "opponent": home_team,
                "opponent_xG": home_xg,
                "home_possession": away_possession,
                "away_possession": home_possession,
                "team_passing": opponent_passing,
                "opponent_passing": team_passing,
                "team_shots_on_target": opponent_shots_on_target,
                "opponent_shots_on_target": team_shots_on_target,
                "total_team_shots": opponent_total_shots,
                "total_opponent_shots": team_total_shots,
            })
driver.quit()
FBref_df = pd.DataFrame(all_data)
print(FBref_df.head())

current_dataset = pd.read_csv('/Users/ifajkhan/Documents/NoFeatureDatabase.csv')

current_dataset["date"] = pd.to_datetime(current_dataset["date"]).dt.strftime('%Y-%m-%d')
FBref_df["date"] = pd.to_datetime(FBref_df["date"]).dt.strftime('%Y-%m-%d')

FBref_df = pd.DataFrame(all_data)

merged_df = current_dataset.merge(FBref_df, on=["date", "team", "opponent"], how="left")


merged_df.to_csv('/Users/ifajkhan/Documents/FeatureDatabase.csv', index=False)






