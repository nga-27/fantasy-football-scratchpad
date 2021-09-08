import datetime
import pprint

import pandas as pd

# Detailed API notes: https://github.com/cwendt94/espn-api/wiki/Football-Intro
from espn_api.football import League

from .config import CONFIG_SETTINGS

LAST_UPDATED = "Last Updated:"
SKIP_ROWS = (LAST_UPDATED, "")
POSITION_ORDER = ["QB", "RB", "RB", "WR", "WR", "TE", "RB/WR/TE", "D/ST", "K"]

def load_schedule(xlsx_dict: dict, LEAGUE, schedule: dict) -> dict:
    LEAGUE.load_teams_from_espn(xlsx_dict['Teams'])
    xlsx_dict['Teams'] = LEAGUE.update_teams_df(xlsx_dict['Teams'])
    team_map = LEAGUE.get_teams()

    date_now = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    for week in schedule["weeks"]:
        key = f"Week {week}"
        xlsx_dict[key] = {"Team": [], "Score": [], "Projected": []}
        xlsx_dict[key]["Team"].append("")
        xlsx_dict[key]["Score"].append("")
        xlsx_dict[key]["Team"].append(LAST_UPDATED)
        xlsx_dict[key]["Score"].append(date_now)
        xlsx_dict[key]["Team"].append("")
        xlsx_dict[key]["Score"].append("")
        xlsx_dict[key]["Projected"].extend(["", "", ""])

        for game in schedule["weeks"][week]:
            team1_key = f"Team {game[0]}"
            team2_key = f"Team {game[1]}"
            team1_name = team_map[team_map[team1_key]["map_id"]]["name"]
            team2_name = team_map[team_map[team2_key]["map_id"]]["name"]
            xlsx_dict[key]["Team"].append(team1_name)
            xlsx_dict[key]["Score"].append(0)
            xlsx_dict[key]["Projected"].append(0)
            xlsx_dict[key]["Team"].append(team2_name)
            xlsx_dict[key]["Score"].append(0)
            xlsx_dict[key]["Projected"].append(0)
            xlsx_dict[key]["Team"].extend(["", ""])
            xlsx_dict[key]["Score"].extend(["", ""])
            xlsx_dict[key]["Projected"].extend(["", ""])

    return xlsx_dict


def update_loaded_schedule(xlsx_dict: dict, LEAGUE) -> dict:
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


def update_scores(xlsx_dict: dict, LEAGUE) -> dict:
    # https://github.com/cwendt94/espn-api/wiki/Football-Intro#get-box-score-of-currentspecific-week
    scores = dict()
    projected = dict()
    current_week = LEAGUE.get_NE().current_week

    # may need to loop to update all scores each week every time?
    for week in range(1, current_week+1):
        str_week = str(week)
        scores[str_week] = dict()
        projected[str_week] = dict()
        ne_box_scores = LEAGUE.get_NE().box_scores(week)
        sw_box_scores = LEAGUE.get_SW().box_scores(week)       

        for game in ne_box_scores:
            home_team = game.home_team.team_name
            away_team = game.away_team.team_name
            scores[str_week][home_team] = game.home_score
            scores[str_week][away_team] = game.away_score

            proj_points = 0.0
            for pos in game.home_lineup:
                if pos.slot_position not in ("BE"):
                    proj_points += pos.projected_points
            projected[str_week][home_team] = proj_points
            proj_points = 0.0
            for pos in game.away_lineup:
                if pos.slot_position not in ("BE"):
                    proj_points += pos.projected_points
            projected[str_week][away_team] = proj_points


        for game in sw_box_scores:
            home_team = game.home_team.team_name
            away_team = game.away_team.team_name
            scores[str_week][home_team] = game.home_score
            scores[str_week][away_team] = game.away_score

            proj_points = 0.0
            for pos in game.home_lineup:
                if pos.slot_position not in ("BE"):
                    proj_points += pos.projected_points
            projected[str_week][home_team] = proj_points
            proj_points = 0.0
            for pos in game.away_lineup:
                if pos.slot_position not in ("BE"):
                    proj_points += pos.projected_points
            projected[str_week][away_team] = proj_points

    for tab in xlsx_dict.keys():
        if 'Week' in tab:
            str_week = tab.split(' ')[1]
            if str_week in scores:
                for i, team in enumerate(xlsx_dict[tab]["Team"]):
                    if team not in SKIP_ROWS:
                        score = scores[str_week][team]
                        xlsx_dict[tab]["Score"][i] = score
                        xlsx_dict[tab]["Projected"][i] = projected[str_week][team]
                    if team == LAST_UPDATED:
                        xlsx_dict[tab]["Score"][i] = \
                            datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

    return xlsx_dict


def update_standings(xlsx_dict: dict, LEAGUE) -> dict:
    standings = load_league_object_records(xlsx_dict, LEAGUE)
    overall_row = 0
    ne_row = 0
    sw_row = 0
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
            f"{LEAGUE.teams[team_id]['stats']['wins']}-{LEAGUE.teams[team_id]['stats']['losses']}"
        xlsx_dict["Standings"]["Pct"][overall_row] = pct
        xlsx_dict["Standings"]["PF"][overall_row] = pf_
        xlsx_dict["Standings"]["PA"][overall_row] = LEAGUE.teams[team_id]['stats']['pa']
        overall_row += 1

    for _, (team_id, pct, pf_) in enumerate(standings):
        region = LEAGUE.teams[team_id]["region"]
        if region == 'NE':
            xlsx_dict["Standings"]["Team"][ne_row] = LEAGUE.teams[team_id]["name"]
            xlsx_dict["Standings"]["Overall Record"][ne_row] = \
                f"{LEAGUE.teams[team_id]['stats']['wins']}-{LEAGUE.teams[team_id]['stats']['losses']}"
            xlsx_dict["Standings"]["Pct"][ne_row] = pct
            xlsx_dict["Standings"]["PF"][ne_row] = pf_
            xlsx_dict["Standings"]["PA"][ne_row] = LEAGUE.teams[team_id]['stats']['pa']
            ne_row += 1

        else:
            xlsx_dict["Standings"]["Team"][sw_row] = LEAGUE.teams[team_id]["name"]
            xlsx_dict["Standings"]["Overall Record"][sw_row] = \
                f"{LEAGUE.teams[team_id]['stats']['wins']}-{LEAGUE.teams[team_id]['stats']['losses']}"
            xlsx_dict["Standings"]["Pct"][sw_row] = pct
            xlsx_dict["Standings"]["PF"][sw_row] = pf_
            xlsx_dict["Standings"]["PA"][sw_row] = LEAGUE.teams[team_id]['stats']['pa']
            sw_row += 1

    return xlsx_dict


def load_league_object_records(xlsx_dict: dict, LEAGUE):
    current_week = LEAGUE.get_NE().current_week
    for tab in xlsx_dict.keys():
        if 'Week' in tab:
            week_num = int(tab.split(' ')[1])
            for i, team in enumerate(xlsx_dict[tab]["Team"]):
                if team not in SKIP_ROWS:
                    map_id = LEAGUE.teams["__team_names__"][team]["map_id"]
                    score = float(xlsx_dict[tab]["Score"][i])
                    LEAGUE.teams[map_id]['stats']['pf'] += score

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
                            else:
                                LEAGUE.teams[map_id2]['stats']['wins'] += 1
                                LEAGUE.teams[map_id]['stats']['losses'] += 1
                                LEAGUE.teams[map_id]['stats']['pa'] += \
                                    float(xlsx_dict[tab]["Score"][i-1])
                                LEAGUE.teams[map_id2]['stats']['pa'] += score

    standings = []
    for team_id in LEAGUE.teams:
        if 'NE-' in team_id or 'SW-' in team_id:
            wins = LEAGUE.teams[team_id]["stats"]["wins"]
            losses = LEAGUE.teams[team_id]["stats"]["losses"]
            if sum([wins, losses]) > 0:
                LEAGUE.teams[team_id]["stats"]["pct"] = float(wins) / float(sum([wins, losses]))
            standings.append(
                (
                    team_id,
                    LEAGUE.teams[team_id]["stats"]["pct"],
                    LEAGUE.teams[team_id]["stats"]["pf"]
                )
            )
    standings = sorted(standings, key=lambda x: (x[1], x[2]), reverse=True)
    return standings


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


class FFLeague():

    def __init__(self):
        self.NE = League(
            league_id=CONFIG_SETTINGS["league_id_ne"],
            year=CONFIG_SETTINGS["year"],
            espn_s2=CONFIG_SETTINGS["espn_s2"],
            swid=CONFIG_SETTINGS["swid"]
        )
        self.SW = League(
            league_id=CONFIG_SETTINGS["league_id_sw"],
            year=CONFIG_SETTINGS["year"],
            espn_s2=CONFIG_SETTINGS["espn_s2"],
            swid=CONFIG_SETTINGS["swid"]
        )
        self.teams = dict()

    def load_teams_from_espn(self, team_data=None):
        if team_data is None:
            return {}

        # To map nicely with ESPN's order, we'll use the "MAP ID"
        for i, _id in enumerate(team_data["MAP ID"]):
            if _id != "":
                self.teams[_id] = {
                    "name": team_data["Team Name"][i],
                    "owner": team_data["Owner"][i],
                    "region": 'NE' if 'NE' in _id else 'SW',
                    "team number": team_data["Team Number"][i],
                    "stats": {
                        "wins": 0,
                        "losses": 0,
                        "pf": 0.0,
                        "pa": 0.0,
                        "pct": 0.0
                    }
                }
                region_id = int(_id.split('-')[1])
                if self.teams[_id]["region"] == 'NE':
                    if self.teams[_id]['name'] != self.NE.teams[region_id-1].team_name:
                        self.teams[_id]['name'] = self.NE.teams[region_id-1].team_name
                else:
                    if self.teams[_id]['name'] != self.SW.teams[region_id-1].team_name:
                        self.teams[_id]['name'] = self.SW.teams[region_id-1].team_name

        # We need the reverse search to map "Team X" to the different divisions
        temp_dict = dict()
        for team_id in self.teams:
            new_key = f"Team {self.teams[team_id]['team number']}"
            temp_dict[new_key] = {
                "map_id": team_id
            }
        self.teams.update(temp_dict)

        # One more reverse search: team_name to map_id
        temp_dict = {"__team_names__": {}}
        for team_id in self.teams:
            if 'Team' not in team_id:
                new_key = self.teams[team_id]["name"]
                temp_dict["__team_names__"][new_key] = {
                    "map_id": team_id
                }
        self.teams.update(temp_dict)

    def update_teams_df(self, team_data: pd.DataFrame) -> pd.DataFrame:
        # pprint.pprint(self.teams)
        for i, team_id in enumerate(team_data["MAP ID"]):
            if team_id == "":
                continue
            team_name = self.teams[team_id]["name"]
            team_data["Team Name"][i] = team_name
        return team_data

    def get_teams(self):
        return self.teams

    def get_NE(self):
        return self.NE

    def get_SW(self):
        return self.SW
        