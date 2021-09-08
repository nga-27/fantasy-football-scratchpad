import datetime

from libs.league import LAST_UPDATED, SKIP_ROWS

def load_schedule(xlsx_dict: dict, LEAGUE, schedule: dict) -> dict:
    LEAGUE.load_teams_from_espn(xlsx_dict['Teams'])
    xlsx_dict['Teams'] = LEAGUE.update_teams_df(xlsx_dict['Teams'])
    team_map = LEAGUE.get_teams()

    date_now = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    for week in schedule["weeks"]:
        key = f"Week {week}"
        xlsx_dict[key] = {"Team": [], "Score": [], "Projected": []}
        xlsx_dict[key]["Team"].append("")
        xlsx_dict[key]["Score"].append("")
        xlsx_dict[key]["Team"].append(LAST_UPDATED)
        xlsx_dict[key]["Score"].append(date_now)
        xlsx_dict[key]["Team"].append("")
        xlsx_dict[key]["Score"].append("")
        xlsx_dict[key]["Projected"].extend(["", "", ""])

        for game in schedule["weeks"][week]:
            team1_key = f"Team {game[0]}"
            team2_key = f"Team {game[1]}"
            team1_name = team_map[team_map[team1_key]["map_id"]]["name"]
            team2_name = team_map[team_map[team2_key]["map_id"]]["name"]
            xlsx_dict[key]["Team"].append(team1_name)
            xlsx_dict[key]["Score"].append(0)
            xlsx_dict[key]["Projected"].append(0)
            xlsx_dict[key]["Team"].append(team2_name)
            xlsx_dict[key]["Score"].append(0)
            xlsx_dict[key]["Projected"].append(0)
            xlsx_dict[key]["Team"].extend(["", ""])
            xlsx_dict[key]["Score"].extend(["", ""])
            xlsx_dict[key]["Projected"].extend(["", ""])

    return xlsx_dict


def update_loaded_schedule(xlsx_dict: dict, LEAGUE) -> dict:
    LEAGUE.load_teams_from_espn(xlsx_dict['Teams'])
    xlsx_dict['Teams'] = LEAGUE.update_teams_df(xlsx_dict['Teams'])
    team_map = LEAGUE.get_teams()
    for tab in xlsx_dict.keys():
        if 'Week' in tab:
            for i, team in enumerate(xlsx_dict[tab]["Team"]):
                if team not in SKIP_ROWS:
                    team_name = team_map[team_map["__team_names__"][team]["map_id"]]["name"]
                    if team != team_name:
                        xlsx_dict[tab]["Team"][i] = team_name
    
    return xlsx_dict