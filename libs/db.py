import json
from pathlib import Path

DB_DIR = Path("internal").resolve()
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "db.json"

DB_DATA = {}


def initialize_db():
    if DB_PATH.exists():
        DB_DATA = json.load(DB_PATH.open('r'))

    
def load_db_if_empty(LEAGUE, reset_db: bool = False):
    if 'teams' not in DB_DATA or reset_db:
        DB_DATA['teams'] = {}
        teams = LEAGUE.get_teams()
        for team_id in teams:
            DB_DATA['teams'][team_id] = teams[team_id]

    if 'rankings' not in DB_DATA or reset_db:
        DB_DATA['rankings'] = {}
        rankings = LEAGUE.get_rankings()
        for rank in rankings:
            DB_DATA['rankings'][rank] = rankings[rank]

    

    
def save_db():
    json.dump(DB_DATA, DB_PATH.open('w'))