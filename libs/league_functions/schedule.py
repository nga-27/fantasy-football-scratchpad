"""schedule.py

Handles scheduling functionality
"""
import datetime

from libs.league import LAST_UPDATED, SKIP_ROWS
from libs.xlsx_utils import xlsx_patch_rows


def load_schedule(xlsx_dict: dict, LEAGUE, schedule: dict) -> dict:
    """load_schedule

    Primarily utilized when calling 'generate_schedule_xlsx.py' as it converts the schedule json
    object to the spreadsheet content.

    Args:
        xlsx_dict (dict): spreadsheet object
        LEAGUE (FFLeague): League object from ESPN API with hooks
        schedule (dict): dict of schedule.json

    Returns:
        dict: xlsx_dict spreadsheet object
    """
    LEAGUE.load_teams_from_espn(xlsx_dict['Teams'])
    xlsx_dict['Teams'] = LEAGUE.update_teams_df(xlsx_dict['Teams'])
    team_map = LEAGUE.get_teams()

    # There are 3 columns to each week: "Team", "Score", and "Projected". This function will provide
    # the required spacing between rows to make this exportable in human-readable format to xlsx.
    date_now = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    for week in schedule["weeks"]:
        key = f"Week {week}"
        xlsx_dict[key] = {"Team": [], "Score": [], "Projected": []}
        xlsx_dict[key] = xlsx_patch_rows(xlsx_dict[key], {}, 1)
        xlsx_dict[key] = xlsx_patch_rows(
            xlsx_dict[key],
            {"Team": LAST_UPDATED, "Score": date_now},
            2
        )

        # The schedule is split up by weeks/tabs of the spreadsheet. For each game in it, format
        # the rows and columns accordingly.
        for game in schedule["weeks"][week]:
            team1_key = f"Team {game[0]}"
            team2_key = f"Team {game[1]}"
            team1_name = team_map[team_map[team1_key]["map_id"]]["name"]
            team2_name = team_map[team_map[team2_key]["map_id"]]["name"]

            patch_obj = {"Team": team1_name, "Score": 0, "Projected": 0}
            xlsx_dict[key] = xlsx_patch_rows(xlsx_dict[key], patch_obj, 1)
            patch_obj["Team"] = team2_name
            xlsx_dict[key] = xlsx_patch_rows(xlsx_dict[key], patch_obj, 3)

    return xlsx_dict


def update_loaded_schedule(xlsx_dict: dict, LEAGUE) -> dict:
    """update_loaded_schedule

    Primarily used in 'run_league_update.py' to update team names as they change over time, since
    that mapping can be difficult.

    Args:
        xlsx_dict (dict): league spreadsheet object
        LEAGUE (FFLeague): League object from ESPN API with hooks

    Returns:
        dict: xlsx_dict spreadsheet object
    """
    LEAGUE.load_teams_from_espn(xlsx_dict['Teams'])
    xlsx_dict['Teams'] = LEAGUE.update_teams_df(xlsx_dict['Teams'])
    team_map = LEAGUE.get_teams()
    for tab in xlsx_dict.keys():
        if 'Week' in tab:
            for i, team in enumerate(xlsx_dict[tab]["Team"]):
                if team not in SKIP_ROWS:
                    team_name = team_map[team_map["__team_names__"][team]["map_id"]]["name"]
                    if team != team_name:
                        xlsx_dict[tab]["Team"][i] = team_name
    
    return xlsx_dict