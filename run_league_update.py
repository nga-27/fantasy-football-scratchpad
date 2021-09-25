"""run_league_update.py

This will be the primary script run to update all scores, rosters, etc. for the "league".
"""
from pathlib import Path
import argparse

from libs.xlsx_utils import load_league_spreadsheet, save_spreadsheet_to_file
from libs.league import FFLeague
from libs.league_functions.schedule import update_loaded_schedule
from libs.league_functions.roster import create_rosters
from libs.league_functions.standings import update_standings
from libs.league_functions.scoring import update_scores
from libs.league_functions.playoffs import manage_playoffs


LEAGUE = FFLeague()


def run_league_update(input_path: Path, output_path: Path, playoff_path: Path):
    """run_league_update

    Primary script run to update the league spreadsheet using ESPN's API calls

    Args:
        input_path (Path): input spreadsheet xlsx path
        output_path (Path): output spreadsheet xlsx path
    """
    league_xlsx = load_league_spreadsheet(input_path)
    league_xlsx = update_loaded_schedule(league_xlsx, LEAGUE)
    league_xlsx = update_scores(league_xlsx, LEAGUE)
    league_xlsx = update_standings(league_xlsx, LEAGUE)
    league_xlsx = create_rosters(league_xlsx, LEAGUE)
    league_xlsx = manage_playoffs(league_xlsx, playoff_path, LEAGUE)

    save_spreadsheet_to_file(league_xlsx, output_path)

    print("*** Done! ***")


if __name__ == "__main__":
    parser = argparse.ArgumentParser("update the league spreadsheet")
    parser.add_argument("--input_path", "-i", required=False,
                        default="content/Mixed-14 Fantasy Football League.xlsx")
    parser.add_argument("--output_path", "-o", required=False,
                        default="output/Mixed-14 Fantasy Football League.xlsx")
    parser.add_argument("--playoff_path", "-p", required=False,
                        default="content/14_team_playoff.json")
    args = parser.parse_args()

    INPUT_PATH = Path(args.input_path).resolve()
    OUTPUT_PATH = Path(args.output_path).resolve()
    PLAYOFF_PATH = Path(args.playoff_path).resolve()

    # create the output directory if it doesn't already exist
    OUTPUT_PATH.parent.mkdir(exist_ok=True)

    run_league_update(INPUT_PATH, OUTPUT_PATH, PLAYOFF_PATH)
