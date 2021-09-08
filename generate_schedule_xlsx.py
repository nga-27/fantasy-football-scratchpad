import os
import json

from libs.xlsx_utils import (
    save_spreadsheet_to_file, load_league_spreadsheet
)
from libs.league import FFLeague
from libs.league_functions.schedule import load_schedule

SCHEDULE_PATH = os.path.join('output', 'schedule.json')

LEAGUE = FFLeague()

def generate_schedule_xlsx():
    if os.path.exists(SCHEDULE_PATH):
        league_xlsx = load_league_spreadsheet()

        with open(SCHEDULE_PATH, 'r') as sch_f:
            schedule_json = json.load(sch_f)

        league_xlsx = load_schedule(league_xlsx, LEAGUE, schedule_json)

        save_spreadsheet_to_file(league_xlsx)


generate_schedule_xlsx()
