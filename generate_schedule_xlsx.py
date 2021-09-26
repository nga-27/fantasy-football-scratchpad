"""generate_schedule_xlsx.py

Function used to reset schedule (for renamed team) and generate schedule for first time in 
xlsx spreadsheet
"""

from pathlib import Path
import json
import argparse

from libs.xlsx_utils import (
    save_spreadsheet_to_file, load_league_spreadsheet
)
from libs.league import FFLeague
from libs.league_functions.schedule import load_schedule
from libs.league_functions.playoffs import manage_playoffs

LEAGUE = FFLeague()


def generate_schedule_xlsx(schedule_path: Path,
                           league_spreadsheet_path: Path,
                           playoff_path: Path,
                           output_path: Path):
    """generate_schedule_xlsx

    Imports the spreadsheet and schedule.json, loads the spreadsheet with the schedule

    Args:
        schedule_path (Path): POSIX-Path to passed-in schedule json
        league_spreadsheet_path (Path): POSIX-path to passed-in league spreadsheet
        playoff_path (Path): POSIX-Path to passed-in playoff json
        output_path (Path): POSIX-path to passed-in generated league spreadsheet
    """
    if schedule_path.exists():
        league_xlsx = load_league_spreadsheet(league_spreadsheet_path)

        with schedule_path.open('r') as sch_f:
            schedule_json = json.load(sch_f)

        league_xlsx = load_schedule(league_xlsx, LEAGUE, schedule_json)
        league_xlsx = manage_playoffs(league_xlsx, playoff_path, LEAGUE)

        save_spreadsheet_to_file(league_xlsx, output_path)

    print("\r\n*** Done! ***")


if __name__ == "__main__":
    parser = argparse.ArgumentParser("update the league schedule")
    parser.add_argument("--schedule_path", "-s", required=False, default="output/schedule.json")
    parser.add_argument("--league_spreadsheet_path", "-l", required=False,
                        default="content/Mixed-14 Fantasy Football League.xlsx")
    parser.add_argument("--league_spreadsheet_output_path", "-o", required=False,
                        default="output/Mixed-14 Fantasy Football League.xlsx")
    parser.add_argument("--playoff_path", "-p", required=False,
                        default="content/14_team_playoff.json")
    args = parser.parse_args()

    SCHEDULE_PATH = Path(args.schedule_path).resolve()
    SPREADSHEET_PATH = Path(args.league_spreadsheet_path).resolve()
    PLAYOFF_PATH = Path(args.playoff_path).resolve()
    OUTPUT_FILE_PATH = Path(args.league_spreadsheet_output_path).resolve()

    generate_schedule_xlsx(SCHEDULE_PATH, SPREADSHEET_PATH, PLAYOFF_PATH, OUTPUT_FILE_PATH)

