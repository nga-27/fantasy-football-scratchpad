import datetime

import pandas as pd

POSITION_ORDER = ["QB", "RB", "RB", "WR", "WR", "TE", "RB/WR/TE", "D/ST", "K"]

def create_rosters(xlsx_dict: dict, LEAGUE) -> dict:
    rosters = {
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
    current_week = LEAGUE.get_NE().current_week
    ne_box_scores = LEAGUE.get_NE().box_scores(current_week)
    sw_box_scores = LEAGUE.get_SW().box_scores(current_week)

    roster_data = {"NE": dict(), "SW": dict()}
    roster_data = generate_roster_data(ne_box_scores, roster_data, "NE")
    roster_data = generate_roster_data(sw_box_scores, roster_data, "SW")

    for team in roster_data["NE"]:
        rosters = load_rosters(rosters, roster_data, "NE", team, LEAGUE)
    for team in roster_data["SW"]:
        rosters = load_rosters(rosters, roster_data, "SW", team, LEAGUE)

    xlsx_dict["Rosters"] = pd.DataFrame.from_dict(rosters)

    return xlsx_dict


def generate_roster_data(box_score, roster_data, region):
    for game in box_score:
        home_team = game.home_team.team_name
        away_team = game.away_team.team_name
        roster_data[region][home_team] = []
        roster_data[region][away_team] = []

        roster_data[region][home_team] = [[]] * len(POSITION_ORDER)
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
                roster_data[region][home_team].append([pos, name, points, proj])

        roster_data[region][away_team] = [[]] * len(POSITION_ORDER)
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
                roster_data[region][away_team].append([pos, name, points, proj])

    return roster_data


def load_rosters(rosters: dict, roster_data: dict, region, team: str, LEAGUE):
    if team in LEAGUE.teams["__team_names__"]:
        map_id = LEAGUE.teams["__team_names__"][team]["map_id"]
        name = LEAGUE.teams[map_id]["owner"]
        rosters[f"{region} Position"].append("")
        rosters[f"{region} Name"].append(team)
        rosters[f"{region} Score"].append(name)
        rosters[f"{region} Projected"].append("")
        if region == "NE":
            rosters["X"].append("")

        for player in roster_data[region][team]:
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