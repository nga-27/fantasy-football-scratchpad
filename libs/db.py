"""db functions
"""

import json
from pathlib import Path
from typing import Union

from .league import FFLeague # pylint:disable=relative-beyond-top-level

DB_DIR = Path("internal").resolve()
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "db.json"

# pylint: disable=invalid-name

class DB():
    """DB Class"""

    def __init__(self):
        """ init DB """
        self.DB_DATA = {}
        if DB_PATH.exists():
            self.DB_DATA = json.load(DB_PATH.open('r'))

    def load_db_if_empty(self, LEAGUE: FFLeague, reset_db: bool = False):
        """ todo: add reset db flag """
        if 'teams' not in self.DB_DATA or reset_db:
            self.load_teams(LEAGUE)
        if 'rankings' not in self.DB_DATA or reset_db:
            self.DB_DATA['rankings'] = {}
            rankings = LEAGUE.get_rankings()
            for rank in rankings:
                self.DB_DATA['rankings'][rank] = rankings[rank]

    def db_set_game(self, week: Union[str,int], game_obj: dict, LEAGUE: FFLeague):
        """ set a game data with scores and projected """
        current_week = LEAGUE.get_info()['current_week']
        if 'teams' not in self.DB_DATA:
            self.load_teams(LEAGUE)
        for team in game_obj:
            if team in LEAGUE.get_teams()["__team_names__"]:
                team_id = LEAGUE.get_teams()["__team_names__"][team]['map_id']
                if 'weeks' not in self.DB_DATA['teams'][team_id]:
                    self.DB_DATA['teams'][team_id]['weeks'] = {}
                if str(week) not in self.DB_DATA['teams'][team_id]['weeks'] or week == current_week:
                    self.DB_DATA['teams'][team_id]['weeks'][str(week)] = game_obj[team]

    def db_get_game(self, week: Union[str,int], team: str, LEAGUE: FFLeague) -> Union[dict,None]:
        """ return a specific game object """
        if week == LEAGUE.get_info()['current_week']:
            return None
        if team not in LEAGUE.get_teams()["__team_names__"]:
            return None
        team_id = LEAGUE.get_teams()["__team_names__"][team]['map_id']
        if 'weeks' not in self.DB_DATA['teams'][team_id]:
            return None
        if str(week) not in self.DB_DATA['teams'][team_id]['weeks']:
            return None
        return self.DB_DATA['teams'][team_id]['weeks'][str(week)]

    def save_db(self):
        """ hard save the db to json """
        json.dump(self.DB_DATA, DB_PATH.open('w'))

    ########################################

    def load_teams(self, LEAGUE):
        """ load team data into db """
        self.DB_DATA['teams'] = {}
        teams = LEAGUE.get_teams()
        for team_id in teams:
            self.DB_DATA['teams'][team_id] = teams[team_id]
