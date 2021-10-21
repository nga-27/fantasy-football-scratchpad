"""run_league_update.py

This will be the primary script run to update all scores, rosters, etc. for the "league".
"""
from pathlib import Path

from libs.config import extract_config_data
from libs.xlsx_utils import load_league_spreadsheet, save_spreadsheet_to_file
from libs.league import FFLeague

from ..league_functions.schedule import update_loaded_schedule
from ..league_functions.roster import create_rosters
from ..league_functions.standings import update_standings
from ..league_functions.scoring import update_scores
from ..league_functions.playoffs import manage_playoffs


def run_league_update(input_path: Path, output_path: Path, config_path: Path):
    """run_league_update

    Primary script run to update the league spreadsheet using ESPN's API calls

    Args:
        input_path (Path): input spreadsheet xlsx path
        output_path (Path): output spreadsheet xlsx path
        config_path (Path): config .json path
    """
    print("Running League Update...")
    LEAGUE = FFLeague()
    league_xlsx = load_league_spreadsheet(input_path)
    config_dict = extract_config_data(config_path)

    league_xlsx = update_loaded_schedule(league_xlsx, LEAGUE)
    league_xlsx = update_scores(league_xlsx, LEAGUE)
    league_xlsx = update_standings(league_xlsx, LEAGUE)
    league_xlsx = create_rosters(league_xlsx, LEAGUE)
    league_xlsx = manage_playoffs(league_xlsx, config_dict['playoffs'], LEAGUE)

    save_spreadsheet_to_file(league_xlsx, output_path, config_dict['config'])

    print("*** League Update - Complete! ***")
