"""xlsx_utils.py

Functions for importing and exporting the league spreadsheet
"""
import os

import pandas as pd
import numpy as np

LEAGUE_XLSX_PATH = os.path.join('content', 'Mixed-14 Fantasy Football League.xlsx')
LEAGUE_OUTPUT_PATH = os.path.join('output', 'Mixed-14 Fantasy Football League.xlsx')

def save_spreadsheet_to_file(data: dict, filename: str=LEAGUE_OUTPUT_PATH):
    """save_spreadsheet_to_file

    Saves the spreadsheet object to the xlsx file

    Args:
        data (dict): spreadsheet file object
        filename (str, optional): file path to output. Defaults to LEAGUE_OUTPUT_PATH.
    """
    with pd.ExcelWriter(filename) as writer:
        for key in data:
            data2 = data[key]
            if isinstance(data[key], dict):
                data2 = pd.DataFrame.from_dict(data[key])

            columns = list(data2.columns)
            if len(columns) > 0:
                data2.set_index(columns[0], inplace=True)
            data2.to_excel(writer, sheet_name=key)


def cleanse_import_sheets(data_sheet: pd.DataFrame) -> pd.DataFrame:
    """cleanse_import_sheets

    Helper function that removes NaNs and empty columns

    Args:
        data_sheet (pd.DataFrame): dataframe to cleanse

    Returns:
        pd.DataFrame: cleansed dataframe
    """
    data_sheet = data_sheet.dropna(axis=1, how='all')
    data_sheet = data_sheet.replace(np.nan, '')
    return data_sheet


def load_league_spreadsheet() -> dict:
    """load_league_spreadsheet

    Opens and imports league spreadsheet into a dictionary object

    Returns:
        dict: league spreadsheet object
    """
    league_xlsx = dict()
    if os.path.exists(LEAGUE_XLSX_PATH):
        xlsx = pd.ExcelFile(LEAGUE_XLSX_PATH)
        for sheet in xlsx.sheet_names:
            league_xlsx[sheet] = xlsx.parse(sheet)
            league_xlsx[sheet] = cleanse_import_sheets(league_xlsx[sheet])
    return league_xlsx
