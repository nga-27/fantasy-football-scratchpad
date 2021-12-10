"""league.py

Primarily housing FFLeague Class as well as some constants related to the league spreadsheet
"""
import pandas as pd

# Detailed API notes: https://github.com/cwendt94/espn-api/wiki/Football-Intro
from espn_api.football import League

from .config import CONFIG_SETTINGS

# pylint: disable=invalid-name

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
        self.info = dict()
        self.playoffs = {"games": {}}

    def load_teams_from_espn(self, team_data: dict = None):
        """load_teams_from_espn

        loads information from Espn to the league object

        Args:
            team_data (dict, optional): xlsx data. Defaults to None.

        Returns:
            None: None
        """
        print(f"{team_data}\r\n")
        if team_data is not None:
            map_teams = [_id for _id in team_data["MAP ID"] if _id != ""]
            map_indexes = [i for i, _id in enumerate(team_data["MAP ID"]) if _id != ""]
            self.info['number_of_teams'] = len(map_teams)
            self.info['current_week'] = self.NE.current_week
            self.info['regular_season'] = {"number_of_weeks": len(map_teams)-1}
            self.info['playoffs'] = {"number_of_weeks": 4}

            # To map nicely with ESPN's order, we'll use the "MAP ID"
            for i, _id in enumerate(map_teams):
                index = map_indexes[i]
                self.teams[_id] = {
                    "name": team_data["Team Name"][index],
                    "owner": team_data["Owner"][index],
                    "region": 'NE' if 'NE' in _id else 'SW',
                    "team number": team_data["Team Number"][index],
                    "stats": {
                        "wins": 0,
                        "losses": 0,
                        "ties": 0,
                        "pf": 0.0,
                        "pa": 0.0,
                        "pct": 0.0
                    },
                    "current_week": {
                        "points": 0.0,
                        "projected": 0.0,
                        "week": self.NE.current_week
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
        """update_teams_df

        maps team name information to team's MAP_ID

        Args:
            team_data (pd.DataFrame): [description]

        Returns:
            pd.DataFrame: [description]
        """
        for i, team_id in enumerate(team_data["MAP ID"]):
            if team_id == "":
                continue
            team_name = self.teams[team_id]["name"]
            team_data["Team Name"][i] = team_name
        return team_data

    def get_teams(self):
        """ return all teams info """
        return self.teams

    def get_NE(self):
        """ return all NE region info """
        return self.NE

    def get_SW(self):
        """ return all SW region info """
        return self.SW

    def get_info(self):
        """ return league configuration info (playoffs, etc.) """
        return self.info

    def set_final_rankings(self, standings_data):
        """ set final rankings in league object """
        self.rankings['by_rank'] = list()
        self.rankings['by_team'] = dict()

        for i, team_tuple in enumerate(standings_data):
            team_id = team_tuple[0]
            obj = {
                "team_id": team_id,
                "name": self.teams[team_id]['name'],
                "owner": self.teams[team_id]['owner'],
                "rank": i+1
            }
            self.rankings['by_rank'].append(obj)
            self.rankings['by_team'][team_id] = obj

    def get_rankings(self):
        """ return rankings object """
        return self.rankings

    def set_team_scores(self, scoring_obj: dict, scoring_type: str = 'points'):
        """ set team scores for current week """
        for team_id in self.teams['__team_names__']:
            if team_id in scoring_obj.keys():
                map_id = self.teams['__team_names__'][team_id]['map_id']
                self.teams[map_id]['current_week'][scoring_type] = scoring_obj[team_id]

    def get_current_week_scores(self, team_id) -> dict:
        """ return current week scores """
        return self.teams[team_id]['current_week']

    def set_playoff_game(self, game_id: str, game_object: list):
        """ set playoff game win-loss-tie """
        self.playoffs[game_id] = {"winner": "", "loser": ""}
        if 'TEAM-RANK' not in game_object[0]['team_name'] and \
            'TEAM-RANK' not in game_object[1]['team_name']:
            team1_id = self.teams["__team_names__"][game_object[0]['team_name']]['map_id']
            team2_id = self.teams["__team_names__"][game_object[1]['team_name']]['map_id']

            if game_object[0]['score'] > game_object[1]['score']:
                self.playoffs[game_id]['winner'] = team1_id
                self.playoffs[game_id]['loser'] = team2_id
            elif game_object[0]['score'] < game_object[1]['score']:
                self.playoffs[game_id]['winner'] = team2_id
                self.playoffs[game_id]['loser'] = team1_id
            else:
                # Tie breaker scenarios begin :O
                content = self.unmanaged_game_tiebreaker(team1_id, team2_id)
                self.playoffs[game_id]['winner'] = content['winner']
                self.playoffs[game_id]['loser'] = content['loser']

    def unmanaged_game_tiebreaker(self, team1_id, team2_id) -> dict:
        """ determine the tie breaker winner """
        # Start with PF
        team1_pf = self.teams[team1_id]['stats']['pf']
        team2_pf = self.teams[team2_id]['stats']['pf']

        if team1_pf > team2_pf:
            return {"winner": team1_id, "loser": team2_id}
        if team1_pf < team2_pf:
            return {"winner": team2_id, "loser": team1_id}

        # Secondary tiebreaker: PA
        team1_pa = self.teams[team1_id]['stats']['pa']
        team2_pa = self.teams[team2_id]['stats']['pa']

        if team1_pa > team2_pa:
            return {"winner": team1_id, "loser": team2_id}
        if team1_pa < team2_pa:
            return {"winner": team2_id, "loser": team1_id}

        print(f"ERROR IN TIEBREAKER!! Teams '{team1_id}' and '{team2_id}' tied through PF/PA")

        return {"winner": team1_id, "loser": team2_id}

    def get_playoffs(self):
        """ return playoffs object """
        return self.playoffs
