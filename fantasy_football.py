"""fantasy_football

Top-level script that runs conditional wrapper scripts to update the league.
"""
from pathlib import Path
import argparse
from shutil import copyfile
from libs.db import DB

from libs.wrappers.schedule_json_generator import generate_schedule
from libs.wrappers.generate_schedule_xlsx import generate_schedule_xlsx
from libs.wrappers.run_league_update import run_league_update

from libs.xlsx_utils import save_archive

# pylint: disable=invalid-name

def fantasy_football(**kwargs):
    """fantasy_football

    Configures and updates the entire league, conditionally. If the schedule file is missing, it
    adds it. If the league needs to be reset due to a team name change, it resets it before updating
    the general part of the league.

    Keyword Args:
        schedule_input_path (Path): raw team txt schedule
        schedule_output_path (Path): becomes "schedule.json"
        league_spreadsheet_input_path (Path): path of sample spreadsheet file for league
        league_spreadsheet_output_path (Path): path of the "final result" spreadsheet for the league
        config_path (Path): json file with playoff and league info
    """
    print("\r\nStarting...")
    SCHEDULE_INPUT_PATH = Path(kwargs.get('schedule_input_path', '')).resolve()
    SCHEDULE_OUTPUT_PATH = Path(kwargs.get('schedule_output_path', '')).resolve()
    SCHEDULE_OUTPUT_PATH.parent.mkdir(exist_ok=True)

    SPREADSHEET_INPUT_PATH = Path(kwargs.get('league_spreadsheet_input_path', '')).resolve()
    CONFIG_PATH = Path(kwargs.get('config_path', '')).resolve()
    SPREADSHEET_OUTPUT_PATH = Path(kwargs.get('league_spreadsheet_output_path', '')).resolve()

    DB_RESET = kwargs.get('db_reset', False)

    if not SCHEDULE_OUTPUT_PATH.exists():
        print("Generating a new 'schedule.json' file...")
        generate_schedule(SCHEDULE_INPUT_PATH, SCHEDULE_OUTPUT_PATH)
        print("*** 'schedule.json' - Created! ***")

    save_archive(SPREADSHEET_OUTPUT_PATH)

    try:
        run_league_update(SPREADSHEET_INPUT_PATH, SPREADSHEET_OUTPUT_PATH, CONFIG_PATH, DB_RESET)

    except KeyError:
        print("Trying a rebase with 'generate_schedule'...")
        generate_schedule_xlsx(
            SCHEDULE_OUTPUT_PATH,
            SPREADSHEET_INPUT_PATH,
            CONFIG_PATH,
            SPREADSHEET_OUTPUT_PATH,
            DB_RESET
        )
        copyfile(SPREADSHEET_OUTPUT_PATH, SPREADSHEET_INPUT_PATH)
        # DB_RESET should always be False on this try, as the DB has already been reset above in 
        # generate_schedule_xlsx
        run_league_update(SPREADSHEET_INPUT_PATH, SPREADSHEET_OUTPUT_PATH, CONFIG_PATH, False)

    print("\r\n*** Done! ***")



if __name__ == "__main__":
    parser = argparse.ArgumentParser("Generate the JSON version of the schedule")
    parser.add_argument("--schedule_input_path", "-i", required=False,
                        default="content/14_team_league_schedule.txt")
    parser.add_argument("--schedule_output_path", "-s", required=False,
                        default="output/schedule.json")
    parser.add_argument("--league_spreadsheet_input_path", "-l", required=False,
                        default="content/Mixed-14_Fantasy_Football_League.xlsx")
    parser.add_argument("--league_spreadsheet_output_path", "-o", required=False,
                        default="output/Mixed-14_Fantasy_Football_League.xlsx")
    parser.add_argument("--config_path", "-c", required=False,
                        default="content/14_team_config.json")
    parser.add_argument("--db_reset", "-d", action='store_true', required=False, default=False)
    args = parser.parse_args()

    fantasy_football(**vars(args))
