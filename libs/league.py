"""league.py

Primarily housing FFLeague Class as well as some constants related to the league spreadsheet
"""
import pandas as pd

# Detailed API notes: https://github.com/cwendt94/espn-api/wiki/Football-Intro
from espn_api.football import League

from .config import CONFIG_SETTINGS


LAST_UPDATED = "Last Updated:"
SKIP_ROWS = (LAST_UPDATED, "")


class FFLeague():
    """FFLeague Class

    League object that houses activity of both leagues and all teams
    """

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
        self.rankings = dict()

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
                    "team number": team_data["Team Number"][i],
                    "stats": {
                        "wins": 0,
                        "losses": 0,
                        "ties": 0,
                        "pf": 0.0,
                        "pa": 0.0,
                        "pct": 0.0
                    }
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
        # pprint.pprint(self.teams)
        for i, team_id in enumerate(team_data["MAP ID"]):
            if team_id == "":
                continue
            team_name = self.teams[team_id]["name"]
            team_data["Team Name"][i] = team_name
        return team_data

    def get_teams(self):
        return self.teams

    def get_NE(self):
        return self.NE

    def get_SW(self):
        return self.SW

    def set_final_rankings(self, standings_data):
        self.rankings['by_rank'] = list()
        self.rankings['by_team'] = dict()

        for i, team_tuple in enumerate(standings_data):
            team_id = team_tuple[0]
            obj = {
                "team_id": team_id,
                "team_name": self.teams[team_id]['name'],
                "owner": self.teams[team_id]['owner'],
                "rank": i+1
            }
            self.rankings['by_rank'].append(obj)
            self.rankings['by_team'][team_id] = obj

    def get_rankings(self):
        return self.rankings
        