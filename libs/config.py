import os
from dotenv import load_dotenv

PWD = os.path.dirname(__file__)
PWD_FUNC, _ = os.path.split(PWD)
DOTENV_PATH = os.path.join(PWD_FUNC, '.env')
if os.path.exists(DOTENV_PATH) is False:
    print(f'WARNING: NO ENVIRONMENT FILE')

load_dotenv(DOTENV_PATH)

CONFIG_SETTINGS = {
    'espn_s2': os.getenv('ESPN_S2', ''),
    'swid': os.getenv('ESPN_SWID', ''),
    'year': int(os.getenv('YEAR', 2021)),
    'league_id_ne': int(os.getenv('LEAGUE_ID_NE', 0)),
    'league_id_sw': int(os.getenv('LEAGUE_ID_SW', 0)),
    'spreadsheet_id': os.getenv('SPREADSHEET_ID', ''),
    'spreadsheet_scopes': os.getenv('SPREADSHEET_SCOPES', [])
}