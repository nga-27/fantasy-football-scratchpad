import copy
import pprint


FORMAT = {
    "Matchup": ["", "", "Bye", ""],
    "Points": ["", "", "", 0.0],
    "Projected": ["", "", "", 0.0]
}

def load_playoffs(xlsx_dict: dict, playoff_data: dict, LEAGUE) -> dict:
    print("playoffs")
    xlsx_dict["Playoffs-Wk1"] = copy.deepcopy(FORMAT)
    xlsx_dict["Playoffs-Wk2"] = copy.deepcopy(FORMAT)
    xlsx_dict["Playoffs-Wk3"] = copy.deepcopy(FORMAT)
    xlsx_dict["Playoffs-Wk4"] = copy.deepcopy(FORMAT)

    return xlsx_dict


def update_playoffs(xlsx_dict: dict, LEAGUE) -> dict:
    pprint.pprint(LEAGUE.get_rankings())
    return xlsx_dict