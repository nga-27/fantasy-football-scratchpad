import datetime

from libs.league import SKIP_ROWS, LAST_UPDATED

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