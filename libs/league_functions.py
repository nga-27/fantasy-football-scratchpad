import datetime
import pprint

import pandas as pd

# Detailed API notes: https://github.com/cwendt94/espn-api/wiki/Football-Intro
from espn_api.football import League

from .config import CONFIG_SETTINGS

LAST_UPDATED = "Last Updated:"

def load_schedule(xlsx_dict: dict, LEAGUE, schedule: dict) -> dict:
    LEAGUE.load_teams_from_espn(xlsx_dict['Teams'])
    xlsx_dict['Teams'] = LEAGUE.update_teams_df(xlsx_dict['Teams'])
    team_map = LEAGUE.get_teams()

    date_now = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    for week in schedule["weeks"]:
        key = f"Week {week}"
        xlsx_dict[key] = {"Team": [], "Score": []}
        xlsx_dict[key]["Team"].append("")
        xlsx_dict[key]["Score"].append("")
        xlsx_dict[key]["Team"].append(LAST_UPDATED)
        xlsx_dict[key]["Score"].append(date_now)
        xlsx_dict[key]["Team"].append("")
        xlsx_dict[key]["Score"].append("")

        for game in schedule["weeks"][week]:
            team1_key = f"Team {game[0]}"
            team2_key = f"Team {game[1]}"
            team1_name = team_map[team_map[team1_key]["map_id"]]["name"]
            team2_name = team_map[team_map[team2_key]["map_id"]]["name"]
            xlsx_dict[key]["Team"].append(team1_name)
            xlsx_dict[key]["Score"].append(0)
            xlsx_dict[key]["Team"].append(team2_name)
            xlsx_dict[key]["Score"].append(0)
            xlsx_dict[key]["Team"].extend(["", ""])
            xlsx_dict[key]["Score"].extend(["", ""])

    return xlsx_dict


def update_loaded_schedule(xlsx_dict: dict, LEAGUE) -> dict:
    LEAGUE.load_teams_from_espn(xlsx_dict['Teams'])
    xlsx_dict['Teams'] = LEAGUE.update_teams_df(xlsx_dict['Teams'])
    team_map = LEAGUE.get_teams()
    for tab in xlsx_dict.keys():
        if 'Week' in tab:
            for i, team in enumerate(xlsx_dict[tab]["Team"]):
                if team not in (LAST_UPDATED, ""):
                    team_name = team_map[team_map["__team_names__"][team]["map_id"]]["name"]
                    if team != team_name:
                        xlsx_dict[tab]["Team"][i] = team_name
    
    return xlsx_dict


class FFLeague():

    def __init__(self):
        self.NE = League(
            league_id=CONFIG_SETTINGS["league_id_ne"],
            year=CONFIG_SETTINGS["year"],
            espn_s2=CONFIG_SETTINGS["espn_s2"],
            swid=CONFIG_SETTINGS["swid"]
        )
        self.SW = League(
            league_id=CONFIG_SETTINGS["league_id_sw"],
            year=CONFIG_SETTINGS["year"],
            espn_s2=CONFIG_SETTINGS["espn_s2"],
            swid=CONFIG_SETTINGS["swid"]
        )
        self.teams = dict()

    def load_teams_from_espn(self, team_data=None):
        if team_data is None:
            return {}

        # To map nicely with ESPN's order, we'll use the "MAP ID"
        for i, _id in enumerate(team_data["MAP ID"]):
            if _id != "":
                self.teams[_id] = {
                    "name": team_data["Team Name"][i],
                    "owner": team_data["Owner"][i],
                    "region": 'NE' if 'NE' in _id else 'SW',
                    "team number": team_data["Team Number"][i]
                }
                region_id = int(_id.split('-')[1])
                if self.teams[_id]["region"] == 'NE':
                    if self.teams[_id]['name'] != self.NE.teams[region_id-1].team_name:
                        self.teams[_id]['name'] = self.NE.teams[region_id-1].team_name
                else:
                    if self.teams[_id]['name'] != self.SW.teams[region_id-1].team_name:
                        self.teams[_id]['name'] = self.SW.teams[region_id-1].team_name

        # We need the reverse search to map "Team X" to the different divisions
        temp_dict = dict()
        for team_id in self.teams:
            new_key = f"Team {self.teams[team_id]['team number']}"
            temp_dict[new_key] = {
                "map_id": team_id
            }
        self.teams.update(temp_dict)

        # One more reverse search: team_name to map_id
        temp_dict = {"__team_names__": {}}
        for team_id in self.teams:
            if 'Team' not in team_id:
                new_key = self.teams[team_id]["name"]
                temp_dict["__team_names__"][new_key] = {
                    "map_id": team_id
                }
        self.teams.update(temp_dict)

    def update_teams_df(self, team_data: pd.DataFrame) -> pd.DataFrame:
        for i, team_id in enumerate(team_data["MAP ID"]):
            if team_id == "":
                continue
            team_name = self.teams[team_id]["name"]
            team_data["Team Name"][i] = team_name
        return team_data

    def get_teams(self):
        return self.teams
        