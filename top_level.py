"""fantasy_football

single function!
"""
import os
import shutil
import datetime
from pathlib import Path
import time
from shutil import copyfile

from dotenv import load_dotenv

from libs.wrappers.schedule_json_generator import generate_schedule
from libs.wrappers.generate_schedule_xlsx import generate_schedule_xlsx
from libs.wrappers.run_league_update import run_league_update

from libs.xlsx_utils import save_archive
from libs.help_function import help_print

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
    SCHEDULE_INPUT_PATH = Path(
        kwargs.get('schedule_input_path', 'content/14_team_league_schedule.txt')).resolve()
    SCHEDULE_OUTPUT_PATH = Path(
        kwargs.get('schedule_output_path', 'output/schedule.json')).resolve()
    SCHEDULE_OUTPUT_PATH.parent.mkdir(exist_ok=True)

    SPREADSHEET_INPUT_PATH = Path(
        kwargs.get('league_spreadsheet_input_path', 'content/Mixed-14_Fantasy_Football_League.xlsx')
    ).resolve()
    CONFIG_PATH = Path(kwargs.get('config_path', 'content/14_team_config.json')).resolve()
    SPREADSHEET_OUTPUT_PATH = Path(
        kwargs.get('league_spreadsheet_output_path', 'output/Mixed-14_Fantasy_Football_League.xlsx')
    ).resolve()

    DB_RESET = kwargs.get('db_reset', False)
    FORCE_RESET = kwargs.get('force_reset', False)
    RUN_HELP = kwargs.get('help_print', False)

    if RUN_HELP:
        help_print()
        return

    if not SCHEDULE_OUTPUT_PATH.exists():
        print("Generating a new 'schedule.json' file...")
        generate_schedule(SCHEDULE_INPUT_PATH, SCHEDULE_OUTPUT_PATH)
        print("*** 'schedule.json' - Created! ***")

    save_archive(SPREADSHEET_OUTPUT_PATH)

    try:
        if FORCE_RESET:
            raise KeyError
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


def league_copier():
    """league_copier

    Since shell commands (such as "cp") are apparently terrible with paths, we'll do it in python!
    """
    SOURCE_PATH = os.getenv("INPUT_SOURCE_PATH", "")
    DEST_PATH = os.getenv("SHARE_DIRECTORY_PATH", "")
    shutil.copy(SOURCE_PATH, DEST_PATH)


def main_cycle():
    print("helloooooooo")
    print(os.getcwd(), type(os.getcwd()))
    print(Path.home(), type(Path.home()))
    if os.getcwd() == str(Path.home()):
        print("changing...")
        os.chdir(Path.home() / "Repos" / "fantasy-football-scratchpad")
    print(os.getcwd())
    load_dotenv()

    END_TIME = os.getenv('CRON_END_TIME', "23:40:00")
    INTERVAL_TIME = int(os.getenv('CRON_FREQUENCY_SEC', "900"))
    print(f"\r\nStop time: {END_TIME}")
    print(f"Interval: {INTERVAL_TIME}")
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    try:
        while current_time < END_TIME:
            print("\r\n----------------")
            print(f"Current time: {current_time}\r\n")

            fantasy_football()
            time.sleep(2)
            print("Copying updated league...")
            league_copier()
            print("Done.")
            time.sleep(INTERVAL_TIME)
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
    except KeyboardInterrupt:
        print("")
        print("Exiting...")
    print("Done.")


if __name__ == "__main__":
    main_cycle()
