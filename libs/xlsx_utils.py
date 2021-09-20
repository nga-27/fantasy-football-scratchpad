"""xlsx_utils.py

Functions for importing and exporting the league spreadsheet
"""
from pathlib import Path

import pandas as pd
import numpy as np


def save_spreadsheet_to_file(data: dict, output_file_path: Path):
    """save_spreadsheet_to_file

    Saves the spreadsheet object to the xlsx file

    Args:
        data (dict): spreadsheet file object
        output_file_path (Path): file path to output.
    """
    with pd.ExcelWriter(output_file_path) as writer:
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


def load_league_spreadsheet(spreadsheet_path: Path) -> dict:
    """load_league_spreadsheet

    Opens and imports league spreadsheet into a dictionary object

    Args:
        spreadsheet_path (Path): file path to the spreadsheet

    Returns:
        dict: league spreadsheet object
    """
    league_xlsx = dict()
    if spreadsheet_path.exists():
        xlsx = pd.ExcelFile(spreadsheet_path)
        for sheet in xlsx.sheet_names:
            league_xlsx[sheet] = cleanse_import_sheets(xlsx.parse(sheet))
    return league_xlsx
