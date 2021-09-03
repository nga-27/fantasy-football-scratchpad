import os
import json
import pandas as pd

from libs.xlsx_utils import save_spreadsheet_to_file, cleanse_import_sheets
from libs.league_functions import load_schedule

LEAGUE_XLSX_PATH = os.path.join('content', 'Mixed-14 Fantasy Football League.xlsx')
LEAGUE_OUTPUT_PATH = os.path.join('output', 'Mixed-14 Fantasy Football League.xlsx')
SCHEDULE_PATH = os.path.join('output', 'schedule.json')


def generate_schedule_xlsx():
    if os.path.exists(LEAGUE_XLSX_PATH) and os.path.exists(SCHEDULE_PATH):
        league_xlsx = {}
        xlsx = pd.ExcelFile(LEAGUE_XLSX_PATH)
        for sheet in xlsx.sheet_names:
            league_xlsx[sheet] = xlsx.parse(sheet)
            league_xlsx[sheet] = cleanse_import_sheets(league_xlsx[sheet])

        with open(SCHEDULE_PATH, 'r') as sch_f:
            schedule_json = json.load(sch_f)

        league_xlsx = load_schedule(league_xlsx, schedule_json)

        save_spreadsheet_to_file(league_xlsx, LEAGUE_OUTPUT_PATH)


generate_schedule_xlsx()
