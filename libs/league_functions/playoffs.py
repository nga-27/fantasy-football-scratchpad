"""playoffs.py

Functions for managing and creating playoffs
"""

import copy
from typing import Union

from libs.xlsx_utils import xlsx_patch_rows
from .bracket import load_bracket # pylint:disable=import-error

# pylint: disable=invalid-name,too-many-locals,too-many-branches,too-many-statements

FORMAT = {
    "Matchup": ["", "", "Byes"],
    "Points": ["", "", ""],
    "Projected": ["", "", ""]
}
BYE_ROW = 2


def manage_playoffs(xlsx_dict: dict, playoff_data: dict, LEAGUE, DB_DATA) -> dict:
    """manage_playoffs

    Main function called to generate all playoff rounds (tabs) as well as the bracket itself

    Args:
        xlsx_dict (dict): league xlsx data object
        playoff_data (dict): config data subset of playoff-related content
        LEAGUE (FFLeague): League object

    Returns:
        dict: xlsx_dict
    """
    xlsx_dict["Playoffs-Wk1"] = copy.deepcopy(FORMAT)
    xlsx_dict = load_round_one(xlsx_dict, playoff_data, LEAGUE, DB_DATA)

    round_range = determine_remaining_rounds(playoff_data)
    for round_num in round_range:
        xlsx_dict[f"Playoffs-Wk{round_num}"] = copy.deepcopy(FORMAT)
        xlsx_dict = load_round_X(xlsx_dict, playoff_data, round_num, LEAGUE, DB_DATA)

    playoff_data = reload_playoff_object(playoff_data, LEAGUE)
    xlsx_dict = load_bracket(xlsx_dict, playoff_data)

    return xlsx_dict


def determine_remaining_rounds(playoff_data: dict) -> list:
    """determine_remaining_rounds

    Returns a list of the remaining rounds after round 1(e.g. [2, 3, 4])

    Args:
        playoff_data (dict): config data subset of playoff-related content

    Returns:
        list: list the remaining rounds of playoffs [after round 1]
    """
    rounds = []
    for key in playoff_data:
        if 'round' in key and key != "round1":
            try:
                round_val = int(key.split('round')[1])
            except ValueError:
                print(f"Error in setting rounds. '{key}' not conducive to conversion to int.")
            rounds.append(round_val)
    return rounds



def load_round_one(xlsx_dict: dict, playoff_data: dict, LEAGUE, DB_DATA) -> dict:
    """load_round_one

    Similar to the 'load_round_X' function below, but handles special cases for round 1 when
    nothing is configured yet

    Args:
        xlsx_dict (dict): league xlsx data object
        playoff_data (dict): config object subset for playoff-related content
        LEAGUE (FFLeague): League object

    Returns:
        dict: xlsx_dict
    """
    round_one = playoff_data['round1']
    dataset = xlsx_dict['Playoffs-Wk1']
    rankings = LEAGUE.get_rankings()
    has_valid_rankings = True
    round_one_week = LEAGUE.get_info()['regular_season']['number_of_weeks'] + 1

    if len(rankings.get('by_rank', [])) == 0 or not is_round_current_or_past(1, LEAGUE):
        num_teams = LEAGUE.get_info().get('number_of_teams')
        rankings['by_rank'] = [{'name': f"TEAM-RANK {i}"} for i in range(1, num_teams+1)]
        has_valid_rankings = False

    for bye in round_one['byes']['teams']:
        # First round will only have int rankings
        team_name = rankings['by_rank'][bye-1]['name']
        if has_valid_rankings:
            team_name = f"({bye}) {team_name}"

        obj_to_patch = {
            "Matchup": team_name
        }
        dataset = xlsx_patch_rows(dataset, obj_to_patch, 1)

    dataset = xlsx_patch_rows(dataset, {}, 2)

    for game in playoff_data['round1']:
        if game != 'byes':
            game_objects = []
            title = playoff_data['round1'][game]['info'].get('name')
            has_titled = False

            for rank in playoff_data['round1'][game]['matchup']:
                team_name = rankings['by_rank'][rank-1]['name']
                if not is_round_current_or_past(1, LEAGUE):
                    scoring = {"points": 0.0, "projected": 0.0}
                elif 'team_id' in rankings['by_rank'][rank-1]:
                    scoring = DB_DATA.db_get_game(
                        round_one_week,
                        rankings['by_rank'][rank-1]['name'],
                        LEAGUE,
                        fetch=True
                    )
                    if scoring is None:
                        scoring = {"points": 0.0, "projected": 0.0}
                    else:
                        scoring = {"points": scoring['score'], "projected": scoring['projected']}
                else:
                    scoring = {"points": 0.0, "projected": 0.0}

                rank_obj = {"rank": rank, "team_name": team_name, "score": scoring["points"]}
                game_objects.append(rank_obj)

                obj_to_patch = {
                    "Matchup": f"({rank}) {team_name}",
                    "Points": scoring["points"],
                    "Projected": scoring["projected"]
                }

                if title and not has_titled:
                    title = f"*** {title} ***"
                    dataset = xlsx_patch_rows(dataset, {"Points": title}, 1)
                    has_titled = True

                dataset = xlsx_patch_rows(dataset, obj_to_patch, 1)
            dataset = xlsx_patch_rows(dataset, {}, 2)
            LEAGUE.set_playoff_game(game, game_objects)

    xlsx_dict['Playoffs-Wk1'] = dataset
    return xlsx_dict


def load_round_X(xlsx_dict: dict, playoff_data: dict, round_num: int, LEAGUE, DB_DATA) -> dict:
    """load_round_X

    Similar to load_round_one, but more generic and assuming other rounds are sequential (2, 3, 4)
    and data is configured with rankings, etc.

    Args:
        xlsx_dict (dict): league xlsx data object
        playoff_data (dict): config object subset of playoff-related content
        round_num (int): which round of playoffs it is, (e.g. 2)
        LEAGUE (FFLeague): League object

    Returns:
        dict: xlsx_dict
    """
    # Assumption is that playoff rounds will go in order: first, second, ...
    round_info = playoff_data[f"round{round_num}"]
    dataset = xlsx_dict[f"Playoffs-Wk{round_num}"]
    total_reg_season_weeks = LEAGUE.get_info()['regular_season']['number_of_weeks']
    playoff_week = total_reg_season_weeks + round_num

    if len(round_info['byes']['teams']) == 0:
        obj_to_patch = {"Matchup": "(none)"}
        dataset = xlsx_patch_rows(dataset, obj_to_patch, 2)

    title = round_info['byes']['info'].get('name')
    has_titled = False
    rankings = LEAGUE.get_rankings()
    for bye in round_info['byes']['teams']:
        # Later round byes are only previous games
        team_id = fetch_team_from_playoff_object(bye, LEAGUE)
        if not is_round_current_or_past(round_num, LEAGUE):
            team_name = f"{bye['game'].upper()} - {bye['type'].upper()}"
        elif team_id in LEAGUE.get_teams():
            team_name = LEAGUE.get_teams()[team_id]['name']
            team_name = f"({rankings['by_team'][team_id]['rank']}) {team_name}"
        else:
            team_name = team_id

        obj_to_patch = {
            "Matchup": team_name
        }

        if title and not has_titled:
            title = f"*** {title} ***"
            dataset['Points'][BYE_ROW] = title
            has_titled = True

        dataset = xlsx_patch_rows(dataset, obj_to_patch, 1)

    dataset = xlsx_patch_rows(dataset, {}, 2)

    for game in round_info:
        if game != "byes":
            game_objects = []
            title = round_info[game]['info'].get('name')
            has_titled = False

            for rank in round_info[game]['matchup']:
                team_id = fetch_team_from_playoff_object(rank, LEAGUE)
                if team_id in LEAGUE.get_teams():
                    team_name = LEAGUE.get_teams()[team_id]['name']
                    scoring = DB_DATA.db_get_game(playoff_week, team_name, LEAGUE, fetch=True)
                    if scoring is None:
                        scoring = {"points": 0.0, "projected": 0.0}
                    else:
                        scoring = {"points": scoring['score'], "projected": scoring['projected']}
                else:
                    team_name = team_id
                    scoring = {"points": 0.0, "projected": 0.0}

                team_view = team_name
                if not is_round_current_or_past(round_num, LEAGUE):
                    team_view = f"Rank - {rank}"
                    if isinstance(rank, dict):
                        team_view = f"{rank['game'].upper()} - {rank['type'].upper()}"
                    scoring = {"points": "", "projected": ""}

                rank_obj = {"rank": rank, "team_name": team_name, "score": scoring["points"]}
                game_objects.append(rank_obj)

                if team_id in LEAGUE.get_teams():
                    team_name = f"({rankings['by_team'][team_id]['rank']}) {team_name}"

                obj_to_patch = {
                    "Matchup": team_view,
                    "Points": scoring["points"],
                    "Projected": scoring["projected"]
                }

                if title and not has_titled:
                    title = f"*** {title} ***"
                    dataset = xlsx_patch_rows(dataset, {"Points": title}, 1)
                    has_titled = True

                dataset = xlsx_patch_rows(dataset, obj_to_patch, 1)
            dataset = xlsx_patch_rows(dataset, {}, 2)
            LEAGUE.set_playoff_game(game, game_objects)
            # pprint.pprint(game_objects)

    xlsx_dict[f'Playoffs-Wk{round_num}'] = dataset

    return xlsx_dict


def fetch_team_from_playoff_object(game_object: Union[dict, int], LEAGUE) -> str:
    """fetch_team_from_playoff_object

    Helper function that converts between 'team_name' and 'team_id' as well as manipulates the
    LEAGUE class to derive wins/losses/tiebreakers for playoff games.

    game_object (when dict): {"game": "g2","type": "winner","default": 4}
        ("game": basically game ID; "type": winner/loser; "default": when playoff games are not
        played yet and unavailable, use default [rank] to fill out spreadsheet tabs)

    Args:
        game_object (Union[dict, int]): either a rank (int) or past game reference (dict)
        LEAGUE (FFLeague): League object

    Returns:
        str: returns either the winner or loser or pure rank of a matched game
    """
    if isinstance(game_object, int):
        # This case happens in round 1 and part of round 2
        if 'by_rank' not in LEAGUE.get_rankings().keys():
            return f"TEAM-RANK {game_object}"
        if 'team_id' not in LEAGUE.get_rankings()['by_rank'][game_object-1]:
            return LEAGUE.get_rankings()['by_rank'][game_object-1]['name']
        return LEAGUE.get_rankings()['by_rank'][game_object-1]['team_id']

    if LEAGUE.get_playoffs()[game_object['game']][game_object['type']] == '':
        # Case where we haven't gotten that far in the season or playoffs to have a team to move
        # forward to the next game.
        return f"TEAM-RANK {game_object['default']}"
    return LEAGUE.get_playoffs()[game_object['game']][game_object['type']]


def reload_playoff_object(playoff_data: dict, LEAGUE) -> dict:
    """reload_playoff_object

    Idea: map team id to game team?

    Args:
        playoff_data (dict): [description]
        LEAGUE ([type]): [description]

    Returns:
        dict: [description]
    """
    # pprint.pprint(LEAGUE.get_playoffs())
    ranks = LEAGUE.get_rankings()['by_rank']
    playoff_round = LEAGUE.get_info()['playoffs']['current_round']
    playoff_data['map'] = {}
    playoff_score_data = LEAGUE.get_playoffs()

    # Map ranks to rank positions in "bracket" object.
    for round_name in playoff_data['bracket']:
        for i, row in enumerate(playoff_data['bracket'][round_name]):
            if 'Rank' in row:
                _, row_info = row.split('Rank')
                row_info = row_info.strip()
                rank_list = row_info.split(' ')
                rank_name = ranks[int(rank_list[0]) - 1]['name']
                if len(rank_list) == 2:
                    rank_name += f" {rank_list[1]}"
                playoff_data['bracket'][round_name][i] = rank_name

    # Map round-by-round information for bracket, when necessary (starting at round 2).
    for round_number in range(2, playoff_round + 1):
        round_key = f"Round {round_number}"
        if round_key in playoff_data['bracket']:
            for i, row in enumerate(playoff_data['bracket'][round_key]):
                if "Game" in row and not "*** Game" in row:
                    row_split = row.split(' ')
                    game_number = int(row_split[1])
                    game_type = row_split[2].lower()
                    game_key = f"g{game_number}"
                    pulled_team = playoff_score_data[game_key][f"{game_type}_name"]
                    if len(row_split) == 4:
                        pulled_team += f" {row_split[3]}"
                    playoff_data['bracket'][round_key][i] = pulled_team

    return playoff_data


def is_round_current_or_past(round_num: int, LEAGUE) -> bool:
    """is_round_current_or_past

    Helper check to determine how far we should move teams forward in the playoffs and when to use
    default values instead of actual teams.

    Args:
        round_num (int): either 1, 2, 3, 4, etc.
        LEAGUE (FFLeague): League class object

    Returns:
        bool: True if is current round or an already played round
    """
    current_week = LEAGUE.get_NE().current_week
    total_reg_season_games = LEAGUE.get_info()['regular_season']['number_of_weeks']
    return current_week >= round_num + total_reg_season_games
