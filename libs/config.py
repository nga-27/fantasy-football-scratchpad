"""config.py

Converts values stored in the .env file to an object referenced by the ESPN API class FFLeague
"""
import os
from dotenv import load_dotenv

PWD = os.path.dirname(__file__)
PWD_FUNC, _ = os.path.split(PWD)
DOTENV_PATH = os.path.join(PWD_FUNC, '.env')
if os.path.exists(DOTENV_PATH) is False:
    print(f'WARNING: NO ENVIRONMENT FILE')

load_dotenv(DOTENV_PATH)

DEFAULT_POSITIONS = ["QB", "RB", "RB", "WR", "WR", "TE", "RB/WR/TE", "D/ST", "K"]
DEFAULT_BENCH = ["BE", "BE", "BE", "BE", "BE", "BE", "IR"]

CONFIG_SETTINGS = {
    'espn_s2': os.getenv('ESPN_S2', ''),
    'swid': os.getenv('ESPN_SWID', ''),
    'year': int(os.getenv('YEAR', 2021)),
    'league_id_ne': int(os.getenv('LEAGUE_ID_NE', 0)),
    'league_id_sw': int(os.getenv('LEAGUE_ID_SW', 0)),
    'position_order': os.getenv('PLAYING_POSITIONS', DEFAULT_POSITIONS),
    'bench_order': os.getenv('BENCH_POSITIONS', DEFAULT_BENCH)
}