import copy
import pprint

from libs.xlsx_utils import xlsx_patch_rows


FORMAT = {
    "Matchup": ["", "", "Bye", ""],
    "Points": ["", "", "", ""],
    "Projected": ["", "", "", ""]
}

def load_playoffs(xlsx_dict: dict, playoff_data: dict, LEAGUE) -> dict:
    xlsx_dict["Playoffs-Wk1"] = copy.deepcopy(FORMAT)
    xlsx_dict = load_round_one(xlsx_dict, playoff_data, LEAGUE)

    xlsx_dict["Playoffs-Wk2"] = copy.deepcopy(FORMAT)
    xlsx_dict["Playoffs-Wk3"] = copy.deepcopy(FORMAT)
    xlsx_dict["Playoffs-Wk4"] = copy.deepcopy(FORMAT)

    return xlsx_dict


def update_playoffs(xlsx_dict: dict, LEAGUE) -> dict:
    pprint.pprint(LEAGUE.get_rankings())
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
        obj_to_patch = {"Matchup": team_name}
        dataset = xlsx_patch_rows(dataset, obj_to_patch, 1)

    dataset = xlsx_patch_rows(dataset, {}, 2)

    return xlsx_dict
