"""scoring.py

Handler for updating scores and projected scores for each week. Referenced API:
https://github.com/cwendt94/espn-api/wiki/Football-Intro#get-box-score-of-currentspecific-week
"""
import datetime
import pprint
from typing import Tuple

from espn_api.football.league import League

from libs.league import SKIP_ROWS, LAST_UPDATED
from libs.db import DB

def update_scores(xlsx_dict: dict, LEAGUE, DB_DATA: DB) -> dict:
    """update_scores

    As named, this function updates scores in real-time based off new information from ESPN's API

    Args:
        xlsx_dict (dict): league spreadsheet object
        LEAGUE (FFLeague): League object from ESPN API with hooks

    Returns:
        dict: xlsx_dict object
    """
    scores = dict()
    projected = dict()
    current_week = LEAGUE.get_NE().current_week

    # Looping for each week. Lists start at 0, football starts at week 1. Add 1 / shift 1 up.
    for week in range(1, current_week+1):
        str_week = str(week)
        scores[str_week] = dict()
        projected[str_week] = dict()     

        # Game-by-game, load the current scores [for all weeks] and projected for applicable weeks.
        scores, projected = load_scores(LEAGUE, scores, projected, week, DB_DATA, 'NE')
        scores, projected = load_scores(LEAGUE, scores, projected, week, DB_DATA, 'SW')

    # Store the current scores as needed for playoffs and rankings.
    LEAGUE.set_team_scores(scores[str(current_week)])
    LEAGUE.set_team_scores(projected[str(current_week)], scoring_type='projected')

    # Update the league spreadsheet object by mapping the score objects to it.
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


def load_scores(league, scores: dict, projected: dict, week, DB_DATA: DB, division: str) -> Tuple[dict,dict]:
    """load_scores

    For each game in a given week, load current/past scores as well as applicable projected scores.

    Args:
        box_score (list): League object from ESPN API with box scores of games
        scores (dict): object housing week and team content for current/past scores
        projected (dict): object housing week and team content for projected scores
        week (int,str): week of evaluation

    Returns:
        Tuple[dict,dict]: return "scores" and "projected" objects
    """
    str_week = week
    if not isinstance(str_week, str):
        str_week = str(str_week)

    if division == 'NE':
        box_score = league.get_NE().box_scores(week)
    else:
        box_score = league.get_SW().box_scores(week)

    for game in box_score:
        home_team = game.home_team.team_name
        away_team = game.away_team.team_name

        home_data = DB_DATA.db_get_game(week, home_team, league)
        if home_data:
            scores[str_week][home_team] = home_data['score']
            projected[str_week][home_team] = home_data['projected']

        else:
            scores[str_week][home_team] = game.home_score

            # For both home and away teams, load projected total points by summing non-bench players.
            proj_points = 0.0
            for pos in game.home_lineup:
                if pos.slot_position not in ("BE"):
                    if pos.game_played > 0:
                        proj_points += pos.points
                    else:
                        proj_points += pos.projected_points
            projected[str_week][home_team] = proj_points

            db_obj = {
                home_team: {
                    "score": scores[str_week][home_team],
                    "projected": projected[str_week][home_team]
                }
            }
            DB_DATA.db_set_game(week, db_obj, league)

        away_data = DB_DATA.db_get_game(week, away_team, league)
        if away_data:
            scores[str_week][away_team] = away_data['score']
            projected[str_week][away_team] = away_data['projected']

        else:
            scores[str_week][away_team] = game.away_score
            proj_points = 0.0
            for pos in game.away_lineup:
                if pos.slot_position not in ("BE"):
                    if pos.game_played > 0:
                        proj_points += pos.points
                    else:
                        proj_points += pos.projected_points
            projected[str_week][away_team] = proj_points

            db_obj = {
                away_team: {
                    "score": scores[str_week][away_team],
                    "projected": projected[str_week][away_team]
                }
            }
            DB_DATA.db_set_game(week, db_obj, league)

    return scores, projected