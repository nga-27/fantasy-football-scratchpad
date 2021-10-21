"""xlsx_utils.py

Functions for importing and exporting the league spreadsheet
"""
import re
import warnings
from pathlib import Path
from typing import Union

import pandas as pd
import numpy as np

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

def save_spreadsheet_to_file(data: dict, output_file_path: Path, config_dict: dict):
    """save_spreadsheet_to_file

    Saves the spreadsheet object to the xlsx file

    Args:
        data (dict): spreadsheet file object
        output_file_path (Path): file path to output.
        config_dict (dict): config subset of config for formatting league spreadsheet
    """
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    with pd.ExcelWriter(output_file_path) as writer: # pylint: disable=abstract-class-instantiated
        for key in data:
            data2 = data[key]
            if isinstance(data[key], dict):
                data2 = pd.DataFrame.from_dict(data[key])

            columns = list(data2.columns)
            if len(columns) > 0:
                data2.set_index(columns[0], inplace=True)
            data2.to_excel(writer, sheet_name=key)

            # I am sick of formatting this constantly, so let's format this so column widths are
            # pretty and readable. Start with index (which is technically column 0, but it doesn't
            # show up on "columns").
            worksheet = writer.sheets[key]
            max_len = find_max_column_width(data2.index, column_name=data2.index.name)
            worksheet.set_column(0, 0, max_len)
            for idx, col in enumerate(data2):
                max_len = find_max_column_width(data2[col], column_name=col)
                # Add one since the index column is technically column 0 and is already done above.
                worksheet.set_column(idx+1, idx+1, max_len)

            if key in config_dict['format']:
                workbook = writer.book # pylint: disable=no-member
                for cell in config_dict['format'][key]:
                    cell_format = workbook.add_format(config_dict['format'][key][cell])
                    value = get_data_from_cell(cell, data2)
                    worksheet.write(cell, value, cell_format)

        writer.save()


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


def find_max_column_width(column: list, column_name: str='') -> int:
    """find_max_column_width

    Of all items in a given column list, find the "longest" item (when casted to a string) so we
    can format the column widths appropriately.

    Args:
        column (list): column to evaluate each item for width by casting item to str and measuring
        column_name (str): name of the column (Default: '')

    Returns:
        int: max length of column + 2
    """
    max_len = len(column_name)
    for item in column:
        if len(str(item)) > max_len:
            max_len = len(str(item))

    return max_len + 2


def xlsx_patch_rows(dataset: dict, patch_obj: dict, num_added_rows: int) -> dict:
    """xlsx_path_rows

    Helper function that fills in empty cells in columns not in patch_obj for num_added_rows. This
    function is helpful in keeping dataframe columns the same size with out tedious .append("")
    clauses everywhere in the code.

    NOTE: patch_obj only applies to first row of num_added_rows, so if num_added_rows > 1, then
    the rest of the rows will be backfilled with empty cells for each column.

    Args:
        dataset (dict): subset of xlsx_dict
        patch_obj (dict): columns (keys) and values to be appended to xlsx_dict (dataset)
        num_added_rows (int): number of empty "" cell rows, typically 1

    Returns:
        dict: dataset, subset of xlsx_dict
    """
    # num_added_rows > 1 only for adding in blank space after content, else one row at a time
    is_first_row = True
    for _ in range(num_added_rows):
        add_spaces = list(dataset.keys())
        if is_first_row:
            for key in patch_obj:
                dataset[key].append(patch_obj[key])
                add_spaces.remove(key)
            is_first_row = False
        for unused_key in add_spaces:
            dataset[unused_key].append("")
    return dataset


def get_data_from_cell(cell: str, dataframe: pd.DataFrame) -> Union[int, float, str]:
    """get_data_from_cell

    This function is primarily to convert an Excel cell name (e.g. 'A1') to a dataframe's column
    name and row number. A few caveats: column 'A' should be the column associated with 0, but in
    fact, the 0th column is df.index, so there's some work with that.

    NOTE: this has not been tested for columns > 'Z', so 'AA' will need some tweaking for it to
    work if that is something that is needed later.

    Args:
        cell (str): 'A1', for example
        dataframe (pd.DataFrame): dataframe representing the Excel sheet

    Returns:
        Union[int, float, str]: whatever the value of that cell is
    """
    xlsx_column_key = "".join(re.findall("[a-zA-Z]+", cell)).upper()
    column_total = 0

    # "A" should be index in columns, "B" is technically first actual 'column' after restructure
    # with set_index in df.
    for char in xlsx_column_key:
        column_total += char.encode('ascii')[0] - 66

    # "A2" is technically dataset index, row 0. "1" is the column header
    xlsx_row_key = int("".join(re.findall("[0-9]+", cell))) - 2
    value = ''
    if column_total == -1:
        return dataframe.index[xlsx_row_key]
    for i, column in enumerate(dataframe.columns):
        if i == column_total:
            return  dataframe[column][xlsx_row_key]

    return value
