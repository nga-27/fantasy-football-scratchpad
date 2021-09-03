"""run_league_update.py

This will be the primary script run to update all scores, rosters, etc. for the "league".
"""
from libs.xlsx_utils import load_league_spreadsheet, save_spreadsheet_to_file
from libs.league_functions import FFLeague, update_loaded_schedule

LEAGUE = FFLeague()

def run_league_update():
    league_xlsx = load_league_spreadsheet()
    LEAGUE.load_teams_from_espn()
    league_xlsx = update_loaded_schedule(league_xlsx, LEAGUE)

    
    save_spreadsheet_to_file(league_xlsx)


run_league_update()
