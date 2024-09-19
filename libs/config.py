"""config.py

Converts values stored in the .env file to an object referenced by the ESPN API class FFLeague
"""
import os
import json
from pathlib import Path
from dotenv import load_dotenv

# pylint: disable=invalid-name

PWD = os.getcwd() #os.path.dirname(__file__)
if PWD == str(Path.home()):
    PWD = os.path.join("Repos", "fantasy-football-scratchpad")
# PWD_FUNC, _ = os.path.split(PWD)
PWD_FUNC = PWD
DOTENV_PATH = os.path.join(PWD_FUNC, '.env')
if os.path.exists(DOTENV_PATH) is False:
    print(f'WARNING: NO ENVIRONMENT FILE. Current PWD: {DOTENV_PATH}')

load_dotenv(DOTENV_PATH)

DEFAULT_POSITIONS = '["QB", "RB", "RB", "WR", "WR", "TE", "RB/WR/TE", "D/ST", "K"]'
DEFAULT_BENCH = '["BE", "BE", "BE", "BE", "BE", "BE", "IR"]'

CONFIG_SETTINGS = {
    'espn_s2': os.getenv('ESPN_S2', ''),
    'swid': os.getenv('ESPN_SWID', ''),
    'year': int(os.getenv('YEAR', '2021')),
    'league_id_ne': int(os.getenv('LEAGUE_ID_NE', '0')),
    'league_id_sw': int(os.getenv('LEAGUE_ID_SW', '0')),
    'position_order': json.loads(os.getenv('PLAYING_POSITIONS', DEFAULT_POSITIONS)),
    'bench_order': json.loads(os.getenv('BENCH_POSITIONS', DEFAULT_BENCH))
}


def extract_config_data(config_path: Path) -> dict:
    """extract_config_data

    Starting in 0.2.0, format and playoff configuration data is stored in a json file. Open the file
    and extract the data to a dictionary

    Args:
        config_path (Path): POSIX-Path object to passed-in config path

    Returns:
        dict: config object containing playoff and formatting info
    """
    if not config_path.exists():
        return {}

    with config_path.open("r") as playoff_f:
        config_data = json.load(playoff_f)
    return config_data
