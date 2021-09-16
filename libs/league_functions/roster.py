"""roster.py

Handler of roster information and updating in real-time
"""
import datetime
import copy

import pandas as pd


POSITION_ORDER = ["QB", "RB", "RB", "WR", "WR", "TE", "RB/WR/TE", "D/ST", "K"]
BENCH_ORDER = ["BE", "BE", "BE", "BE", "BE", "BE", "IR"]
ROSTER = {
        "NE Position": ["", "Date Updated:", "", ""],
        "NE Name": ["", datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S"), "", ""],
        "NE Score": ["", "", "", ""],
        "NE Projected": ["", "", "", ""],
        "X": ["", "", "", ""],
        "SW Position": ["", "", "", ""],
        "SW Name": ["", "", "", ""],
        "SW Score": ["", "", "", ""],
        "SW Projected": ["", "", "", ""]
    }


def create_rosters(xlsx_dict: dict, LEAGUE) -> dict:
    """create_rosters

    Pulls player information, storing them for each team with slotted position (bench or otherwise),
    name, points for the week, and projected points for the week.

    Args:
        xlsx_dict (dict): league spreadsheet object
        LEAGUE (FFLeague): League object from ESPN API with hooks

    Returns:
        dict: xlsx_dict spreadsheet object
    """
    rosters = copy.deepcopy(ROSTER)

    # Rosters are updated only on the current week, so pull that league information.
    current_week = LEAGUE.get_NE().current_week
    ne_box_scores = LEAGUE.get_NE().box_scores(current_week)
    sw_box_scores = LEAGUE.get_SW().box_scores(current_week)

    # Load the all roster data in order of POSITION_ORDER from both leagues 
    roster_data = {"NE": dict(), "SW": dict()}
    roster_data = generate_roster_data(ne_box_scores, roster_data, "NE")
    roster_data = generate_roster_data(sw_box_scores, roster_data, "SW")

    # Map the raw data to rosters object with proper empty-string spacing between rows to be
    # converted to a pandas dataframe to be written to xlsx
    for team in roster_data["NE"]:
        rosters = load_rosters(rosters, roster_data, "NE", team, LEAGUE)
    for team in roster_data["SW"]:
        rosters = load_rosters(rosters, roster_data, "SW", team, LEAGUE)

    xlsx_dict["Rosters"] = pd.DataFrame.from_dict(rosters)

    return xlsx_dict


def generate_roster_data(box_score: list, roster_data: dict, region: str) -> dict:
    """generate_roster_data

    Subfunction loading each league's teams' roster information.

    Args:
        box_score (list): FFLeague subobject, list of games per league
        roster_data (dict): region-based object storing roster information
        region (str): either "NE" or "SW"

    Returns:
        dict: roster_data
    """
    for game in box_score:
        home_team = game.home_team.team_name
        away_team = game.away_team.team_name
        roster_data[region][home_team] = []
        roster_data[region][away_team] = []

        # Load the player positions based off POSITION_ORDER as lists of lists (to be mapped later).
        roster_data[region][home_team] = [[]] * (len(POSITION_ORDER) + len(BENCH_ORDER))
        print(len(roster_data[region][home_team]))
        for player in game.home_lineup:
            pos = player.slot_position
            name = player.name
            points = player.points
            proj = player.projected_points
            if pos in POSITION_ORDER:
                if roster_data[region][home_team][POSITION_ORDER.index(pos)] != []:
                    roster_data[region][home_team][POSITION_ORDER.index(pos) + 1] = \
                        [pos, name, points, proj]
                else:
                    roster_data[region][home_team][POSITION_ORDER.index(pos)] = \
                        [pos, name, points, proj]
            else:
                for i in range(6):
                    if len(roster_data[region][home_team][BENCH_ORDER.index(pos)+len(POSITION_ORDER)+i]) == 0:
                        roster_data[region][home_team][BENCH_ORDER.index(pos)+len(POSITION_ORDER)+i] = \
                            [pos, name, points, proj]
                        break

                roster_data[region][home_team].append([pos, name, points, proj])

        # Load the player positions based off POSITION_ORDER as lists of lists (to be mapped later).
        roster_data[region][away_team] = [[]] * (len(POSITION_ORDER) + len(BENCH_ORDER))
        print(len(roster_data[region][away_team]))
        for player in game.away_lineup:
            pos = player.slot_position
            name = player.name
            points = player.points
            proj = player.projected_points
            if pos in POSITION_ORDER:
                if roster_data[region][away_team][POSITION_ORDER.index(pos)] != []:
                    roster_data[region][away_team][POSITION_ORDER.index(pos) + 1] = \
                        [pos, name, points, proj]
                else:
                    roster_data[region][away_team][POSITION_ORDER.index(pos)] = \
                        [pos, name, points, proj]
            else:
                for i in range(6):
                    if len(roster_data[region][away_team][BENCH_ORDER.index(pos)+len(POSITION_ORDER)+i]) == 0:
                        roster_data[region][away_team][BENCH_ORDER.index(pos)+len(POSITION_ORDER)+i] = \
                            [pos, name, points, proj]
                        break

    return roster_data


def load_rosters(rosters: dict, roster_data: dict, region: str, team: str, LEAGUE) -> dict:
    """load_rosters

    Converts queried roster data to organized roster info in order of positions with related data.

    Args:
        rosters (dict): main rosters object to be stored in league spreadsheet
        roster_data (dict): raw roster data object from 'generate_roster_data'
        region (str): either "NE" or "SW"
        team (str): team name
        LEAGUE (FFLeague): League object from ESPN API with hooks

    Returns:
        dict: rosters
    """
    # We need to make this check to avoid the robots getting passed to this object. Map the listed
    # data from above to a dictionary with the proper spaces in rows and correct columns to become
    # the pandas dataframe object for the "Rosters" tab of the spreadsheet. Do this for both regions 
    if team in LEAGUE.teams["__team_names__"]:
        map_id = LEAGUE.teams["__team_names__"][team]["map_id"]
        name = LEAGUE.teams[map_id]["owner"]
        rosters[f"{region} Position"].append("")
        rosters[f"{region} Name"].append(team)
        rosters[f"{region} Score"].append(name)
        rosters[f"{region} Projected"].append("")
        
        # The "X" column is a simple column spacer between the leagues. We only want to add this
        # once, so let's just operate on them when the NE region fires.
        if region == "NE":
            rosters["X"].append("")

        for _, player in enumerate(roster_data[region][team]):
            if len(player) == 0:
                # Case where a lineup position is empty
                player = ["", "", 0.0, 0.0]
            rosters[f"{region} Position"].append(player[0])
            rosters[f"{region} Name"].append(player[1])
            rosters[f"{region} Score"].append(player[2])
            rosters[f"{region} Projected"].append(player[3])
            if region == "NE":
                rosters["X"].append("")

        rosters[f"{region} Position"].extend(["", ""])
        rosters[f"{region} Name"].extend(["", ""])
        rosters[f"{region} Score"].extend(["", ""])
        rosters[f"{region} Projected"].extend(["", ""])
        if region == "NE":
            rosters["X"].extend(["", ""])
    return rosters