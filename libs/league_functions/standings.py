"""standings.py

Handles updating standings including wins, losses, points for (PF), points against (PA), and winning
percentages. This also shows how the leagues and the overall standings map.
"""
from libs.league import SKIP_ROWS


def update_standings(xlsx_dict: dict, LEAGUE) -> dict:
    """update_standings

    Top-level function for creating the standings object

    Args:
        xlsx_dict (dict): league spreadsheet object
        LEAGUE (FFLeague): League object from ESPN API with hooks

    Returns:
        dict: xlsx_dict spreadsheet object
    """
    standings = load_league_object_records(xlsx_dict, LEAGUE)
    overall_row = 0
    ne_row = 0
    sw_row = 0

    # We are trying to find the correct rows to start loading the spreadsheet object. Loop through
    # until the various trigger words are found in the "Region Rank" column of the "Standings" tab.
    # We are also maintaining 3 row counters: overall_row, sw_row, and ne_row. The first is for the
    # entire standings page, including the overall rankings of all 14 teams. The latter two are to
    # keep track of where the individual regions/leagues exist on the page and load them accordingly
    while overall_row < len(xlsx_dict["Standings"]["Region Rank"]) and \
        xlsx_dict["Standings"]["Region Rank"][overall_row] != "OVERALL":
        if xlsx_dict["Standings"]["Region Rank"][overall_row] == "NORTHEAST":
            ne_row = overall_row + 1
        if xlsx_dict["Standings"]["Region Rank"][overall_row] == "SOUTHWEST":
            sw_row = overall_row + 1
        overall_row += 1

    overall_row += 1
    for _, (team_id, pct, pf_) in enumerate(standings):
        xlsx_dict["Standings"]["Team"][overall_row] = LEAGUE.teams[team_id]["name"]
        xlsx_dict["Standings"]["Overall Record"][overall_row] = \
            f"{LEAGUE.teams[team_id]['stats']['wins']}-" + \
            f"{LEAGUE.teams[team_id]['stats']['losses']}-" + \
            f"{LEAGUE.teams[team_id]['stats']['ties']}"
        xlsx_dict["Standings"]["Pct"][overall_row] = pct
        xlsx_dict["Standings"]["PF"][overall_row] = pf_
        xlsx_dict["Standings"]["PA"][overall_row] = LEAGUE.teams[team_id]['stats']['pa']
        overall_row += 1

    for _, (team_id, pct, pf_) in enumerate(standings):
        region = LEAGUE.teams[team_id]["region"]
        if region == 'NE':
            xlsx_dict["Standings"]["Team"][ne_row] = LEAGUE.teams[team_id]["name"]
            xlsx_dict["Standings"]["Overall Record"][ne_row] = \
                f"{LEAGUE.teams[team_id]['stats']['wins']}-" + \
                f"{LEAGUE.teams[team_id]['stats']['losses']}-" + \
                f"{LEAGUE.teams[team_id]['stats']['ties']}"
            xlsx_dict["Standings"]["Pct"][ne_row] = pct
            xlsx_dict["Standings"]["PF"][ne_row] = pf_
            xlsx_dict["Standings"]["PA"][ne_row] = LEAGUE.teams[team_id]['stats']['pa']
            ne_row += 1

        else:
            xlsx_dict["Standings"]["Team"][sw_row] = LEAGUE.teams[team_id]["name"]
            xlsx_dict["Standings"]["Overall Record"][sw_row] = \
                f"{LEAGUE.teams[team_id]['stats']['wins']}-" + \
                f"{LEAGUE.teams[team_id]['stats']['losses']}-" + \
                f"{LEAGUE.teams[team_id]['stats']['ties']}"
            xlsx_dict["Standings"]["Pct"][sw_row] = pct
            xlsx_dict["Standings"]["PF"][sw_row] = pf_
            xlsx_dict["Standings"]["PA"][sw_row] = LEAGUE.teams[team_id]['stats']['pa']
            sw_row += 1

    return xlsx_dict


def load_league_object_records(xlsx_dict: dict, LEAGUE):
    """load_league_object_records

    Before setting the spreadsheet, we update the LEAGUE object with the wins/losses/etc. data

    Args:
        xlsx_dict (dict): league spreadsheet object
        LEAGUE (FFLeague): League object from ESPN API with hooks

    Returns:
        list: overall/all standings list, sorted by highest winning pct then points for
    """
    current_week = LEAGUE.get_NE().current_week
    for tab in xlsx_dict.keys():
        if 'Week' in tab:
            week_num = int(tab.split(' ')[1])

            for i, team in enumerate(xlsx_dict[tab]["Team"]):
                if team not in SKIP_ROWS:
                    map_id = LEAGUE.teams["__team_names__"][team]["map_id"]
                    score = float(xlsx_dict[tab]["Score"][i])
                    LEAGUE.teams[map_id]['stats']['pf'] += score

                    # For games played in the past week(s), trigger wins/losses/ties.
                    if week_num < current_week:
                        if xlsx_dict[tab]["Team"][i-1] not in SKIP_ROWS:
                            # 2nd team in the pairing
                            team2 = xlsx_dict[tab]["Team"][i-1]
                            map_id2 = LEAGUE.teams["__team_names__"][team2]["map_id"]

                            if score > float(xlsx_dict[tab]["Score"][i-1]):
                                LEAGUE.teams[map_id]['stats']['wins'] += 1
                                LEAGUE.teams[map_id2]['stats']['losses'] += 1
                                LEAGUE.teams[map_id]['stats']['pa'] += \
                                    float(xlsx_dict[tab]["Score"][i-1])
                                LEAGUE.teams[map_id2]['stats']['pa'] += score

                            elif score == float(xlsx_dict[tab]["Score"][i-1]):
                                LEAGUE.teams[map_id]['stats']['ties'] += 1
                                LEAGUE.teams[map_id2]['stats']['ties'] += 1
                                LEAGUE.teams[map_id]['stats']['pa'] += \
                                    float(xlsx_dict[tab]["Score"][i-1])
                                LEAGUE.teams[map_id2]['stats']['pa'] += score

                            else:
                                LEAGUE.teams[map_id2]['stats']['wins'] += 1
                                LEAGUE.teams[map_id]['stats']['losses'] += 1
                                LEAGUE.teams[map_id]['stats']['pa'] += \
                                    float(xlsx_dict[tab]["Score"][i-1])
                                LEAGUE.teams[map_id2]['stats']['pa'] += score

    # Ready the standings for ordering.
    standings = []
    for team_id in LEAGUE.teams:
        if 'NE-' in team_id or 'SW-' in team_id:
            wins = LEAGUE.teams[team_id]["stats"]["wins"]
            losses = LEAGUE.teams[team_id]["stats"]["losses"]
            ties = LEAGUE.teams[team_id]["stats"]["ties"]
            if sum([wins, losses, ties]) > 0:
                win_sum = (1.0 * wins) + (0.5 * ties) + (0.0 * losses) 
                LEAGUE.teams[team_id]["stats"]["pct"] = \
                    float(win_sum) / float(sum([wins, losses, ties]))
            standings.append(
                (
                    team_id,
                    LEAGUE.teams[team_id]["stats"]["pct"],
                    LEAGUE.teams[team_id]["stats"]["pf"]
                )
            )
    standings = sorted(standings, key=lambda x: (x[1], x[2]), reverse=True)
    return standings