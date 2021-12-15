"""generate_schedule_xlsx.py

Function used to reset schedule (for renamed team) and generate schedule for first time in
xlsx spreadsheet
"""

from pathlib import Path
import json

from libs.xlsx_utils import (
    save_spreadsheet_to_file, load_league_spreadsheet
)
from libs.config import extract_config_data
from libs.league import FFLeague
from libs.db import DB

from ..league_functions.schedule import load_schedule
from ..league_functions.playoffs import manage_playoffs

# pylint: disable=invalid-name

def generate_schedule_xlsx(schedule_path: Path,
                           league_spreadsheet_path: Path,
                           config_path: Path,
                           output_path: Path):
    """generate_schedule_xlsx

    Imports the spreadsheet and schedule.json, loads the spreadsheet with the schedule

    Args:
        schedule_path (Path): POSIX-Path to passed-in schedule json
        league_spreadsheet_path (Path): POSIX-path to passed-in league spreadsheet
        config_path (Path): POSIX-Path to passed-in config json
        output_path (Path): POSIX-path to passed-in generated league spreadsheet
    """
    print("Generating Schedule XLSX...")
    if schedule_path.exists():
        LEAGUE = FFLeague()
        DB_DATA = DB()
        league_xlsx = load_league_spreadsheet(league_spreadsheet_path)

        with schedule_path.open('r') as sch_f:
            schedule_json = json.load(sch_f)

        league_xlsx = load_schedule(league_xlsx, LEAGUE, schedule_json)
        config_dict = extract_config_data(config_path)
        league_xlsx = manage_playoffs(league_xlsx, config_dict['playoffs'], LEAGUE, DB_DATA)

        save_spreadsheet_to_file(league_xlsx, output_path, config_dict['config'])

    print("*** Generate Schedule XLSX - Complete! ***")
