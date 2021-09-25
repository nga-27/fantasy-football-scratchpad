import copy
import json
from pathlib import Path
import pprint

from libs.xlsx_utils import xlsx_patch_rows


FORMAT = {
    "Matchup": ["", "", "Byes"],
    "Points": ["", "", ""],
    "Projected": ["", "", ""]
}


def manage_playoffs(xlsx_dict: dict, playoff_path: Path, LEAGUE) -> dict:
    if playoff_path.exists():
        with playoff_path.open("r") as playoff_f:
            playoff_data = json.load(playoff_f)
            xlsx_dict["Playoffs-Wk1"] = copy.deepcopy(FORMAT)
            xlsx_dict = load_round_one(xlsx_dict, playoff_data, LEAGUE)

            xlsx_dict["Playoffs-Wk2"] = copy.deepcopy(FORMAT)
            xlsx_dict["Playoffs-Wk3"] = copy.deepcopy(FORMAT)
            xlsx_dict["Playoffs-Wk4"] = copy.deepcopy(FORMAT)
    return xlsx_dict


def load_round_one(xlsx_dict: dict, playoff_data: dict, LEAGUE) -> dict:
    round_one = playoff_data['round1']
    dataset = xlsx_dict['Playoffs-Wk1']
    rankings = LEAGUE.get_rankings()

    if len(rankings.get('by_rank', [])) == 0:
        rankings['by_rank'] = [{'name': f"TEAM-RANK {i}"} for i in range(1,15)]

    for bye in round_one['byes']:
        # First round will only have int rankings
        team_name = rankings['by_rank'][bye-1]['name']
        obj_to_patch = {
            "Matchup": team_name
        }
        dataset = xlsx_patch_rows(dataset, obj_to_patch, 1)

    dataset = xlsx_patch_rows(dataset, {}, 2)

    for game in playoff_data['round1']:
        if game != 'byes':
            for rank in playoff_data['round1'][game]:
                team_name = rankings['by_rank'][rank-1]['name']
                if 'team_id' in rankings['by_rank'][rank-1]:
                    scoring = LEAGUE.get_current_week_scores(rankings['by_rank'][rank-1]['team_id'])
                else:
                    scoring = {"points": 0.0, "projected": 0.0}

                obj_to_patch = {
                    "Matchup": team_name,
                    "Points": scoring["points"],
                    "Projected": scoring["projected"]
                }
                dataset = xlsx_patch_rows(dataset, obj_to_patch, 1)
            dataset = xlsx_patch_rows(dataset, {}, 2)

    xlsx_dict['Playoffs-Wk1'] = dataset
    return xlsx_dict
