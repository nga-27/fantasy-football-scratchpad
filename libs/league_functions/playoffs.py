import copy
import json
from pathlib import Path
from typing import Tuple

from libs.xlsx_utils import xlsx_patch_rows
from .bracket import load_bracket

FORMAT = {
    "Matchup": ["", "", "Byes"],
    "Points": ["", "", ""],
    "Projected": ["", "", ""]
}
BYE_ROW = 2


def manage_playoffs(xlsx_dict: dict, playoff_path: Path, LEAGUE) -> dict:
    if not playoff_path.exists():
        return xlsx_dict
    
    with playoff_path.open("r") as playoff_f:
        playoff_data = json.load(playoff_f)

    xlsx_dict["Playoffs-Wk1"] = copy.deepcopy(FORMAT)
    xlsx_dict = load_round_one(xlsx_dict, playoff_data, LEAGUE)

    round_range = determine_remaining_rounds(playoff_data)
    for round_num in round_range:
        xlsx_dict[f"Playoffs-Wk{round_num}"] = copy.deepcopy(FORMAT)
        xlsx_dict = load_round_X(xlsx_dict, playoff_data, round_num, LEAGUE)

    xlsx_dict = load_bracket(xlsx_dict, playoff_data)

    return xlsx_dict


def determine_remaining_rounds(playoff_data: dict) -> list:
    # Returns a list of the remaining rounds
    rounds = []
    for key in playoff_data:
        if 'round' in key and key != "round1":
            try:
                round_val = int(key.split('round')[1])
            except ValueError:
                print(f"Error in setting rounds. '{key}' not conducive to conversion to int.")
            rounds.append(round_val)
    return rounds



def load_round_one(xlsx_dict: dict, playoff_data: dict, LEAGUE) -> dict:
    round_one = playoff_data['round1']
    dataset = xlsx_dict['Playoffs-Wk1']
    rankings = LEAGUE.get_rankings()
    has_valid_rankings = True

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
                    scoring = LEAGUE.get_current_week_scores(rankings['by_rank'][rank-1]['team_id'])
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


def load_round_X(xlsx_dict: dict, playoff_data: dict, round_num: int, LEAGUE) -> dict:
    # Assumption is that playoff rounds will go in order: first, second, ...
    round_info = playoff_data[f"round{round_num}"]
    dataset = xlsx_dict[f"Playoffs-Wk{round_num}"]

    if len(round_info['byes']['teams']) == 0:
        obj_to_patch = {"Matchup": "(none)"}
        dataset = xlsx_patch_rows(dataset, obj_to_patch, 1)

    title = round_info['byes']['info'].get('name')
    has_titled = False
    rankings = LEAGUE.get_rankings()
    for bye in round_info['byes']['teams']:
        # Later round byes are only previous games
        team_id = fetch_team_from_playoff_object(bye, LEAGUE)
        if not is_round_current_or_past(round_num, LEAGUE):
            team_name = team_id
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
                    scoring = LEAGUE.get_current_week_scores(team_id)
                else:
                    team_name = team_id
                    scoring = {"points": 0.0, "projected": 0.0}

                rank_obj = {"rank": rank, "team_name": team_name, "score": scoring["points"]}
                game_objects.append(rank_obj)

                if team_id in LEAGUE.get_teams():
                    team_name = f"({rankings['by_team'][team_id]['rank']}) {team_name}"

                obj_to_patch = {
                    "Matchup": team_name,
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

    xlsx_dict[f'Playoffs-Wk{round_num}'] = dataset

    return xlsx_dict


def fetch_team_from_playoff_object(game_object: Tuple[dict, int], LEAGUE) -> str:
    if isinstance(game_object, int):
        if 'by_rank' not in LEAGUE.get_rankings().keys():
            return f"TEAM-RANK {game_object}"
        elif 'team_id' not in LEAGUE.get_rankings()['by_rank'][game_object-1]:
            return LEAGUE.get_rankings()['by_rank'][game_object-1]['name']
        else:
            return LEAGUE.get_rankings()['by_rank'][game_object-1]['team_id']

    if LEAGUE.get_playoffs()[game_object['game']][game_object['type']] == '':
        return f"TEAM-RANK {game_object['default']}"
    return LEAGUE.get_playoffs()[game_object['game']][game_object['type']]


def is_round_current_or_past(round_num: int, LEAGUE) -> bool:
    current_week = LEAGUE.get_NE().current_week
    total_reg_season_games = LEAGUE.get_info()['regular_season']['number_of_weeks']
    return current_week >= round_num + total_reg_season_games
