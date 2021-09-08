"""run_league_update.py

This will be the primary script run to update all scores, rosters, etc. for the "league".
"""
from libs.xlsx_utils import load_league_spreadsheet, save_spreadsheet_to_file
from libs.league import FFLeague
from libs.league_functions.schedule import update_loaded_schedule
from libs.league_functions.roster import create_rosters
from libs.league_functions.standings import update_standings
from libs.league_functions.scoring import update_scores

LEAGUE = FFLeague()

def run_league_update():
    league_xlsx = load_league_spreadsheet()
    league_xlsx = update_loaded_schedule(league_xlsx, LEAGUE)
    league_xlsx = update_scores(league_xlsx, LEAGUE)
    league_xlsx = update_standings(league_xlsx, LEAGUE)
    league_xlsx = create_rosters(league_xlsx, LEAGUE)

    save_spreadsheet_to_file(league_xlsx)


run_league_update()
