import json
from pathlib import Path

from .league import FFLeague

DB_PATH = Path("internal/db.json").resolve()
DB_PATH.mkdir(exist_ok=True)


def initialize_db(LEAGUE: FFLeague):
    db_data = {}
    if DB_PATH.exists():
        db_data = json.load(DB_PATH.open('r'))

    print(LEAGUE.get_teams())