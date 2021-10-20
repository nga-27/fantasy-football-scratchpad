from pathlib import Path
import argparse
from shutil import copyfile

from scripts.schedule_json_generator import generate_schedule
from scripts.generate_schedule_xlsx import generate_schedule_xlsx
from scripts.run_league_update import run_league_update


def fantasy_football(**kwargs):
    print("\r\nStarting...")
    SCHEDULE_INPUT_PATH = Path(kwargs.get('schedule_input_path', '')).resolve()
    SCHEDULE_OUTPUT_PATH = Path(kwargs.get('schedule_output_path', '')).resolve()
    SCHEDULE_OUTPUT_PATH.parent.mkdir(exist_ok=True)

    SPREADSHEET_INPUT_PATH = Path(kwargs.get('league_spreadsheet_input_path', '')).resolve()
    CONFIG_PATH = Path(kwargs.get('config_path', '')).resolve()
    SPREADSHEET_OUTPUT_PATH = Path(kwargs.get('league_spreadsheet_output_path', '')).resolve()

    if not SCHEDULE_OUTPUT_PATH.exists():
        generate_schedule(SCHEDULE_INPUT_PATH, SCHEDULE_OUTPUT_PATH)

    try:
        run_league_update(SPREADSHEET_INPUT_PATH, SPREADSHEET_OUTPUT_PATH, CONFIG_PATH)

    except:
        print("Trying a rebase with 'generate_schedule'...")
        generate_schedule_xlsx(SCHEDULE_OUTPUT_PATH, SPREADSHEET_INPUT_PATH, CONFIG_PATH, SPREADSHEET_OUTPUT_PATH)
        copyfile(SPREADSHEET_OUTPUT_PATH, SPREADSHEET_INPUT_PATH)
        run_league_update(SPREADSHEET_INPUT_PATH, SPREADSHEET_OUTPUT_PATH, CONFIG_PATH)



if __name__ == "__main__":
    parser = argparse.ArgumentParser("Generate the JSON version of the schedule")
    parser.add_argument("--schedule_input_path", "-i", required=False, default="content/14_team_league_schedule.txt")
    parser.add_argument("--schedule_output_path", "-s", required=False, default="output/schedule.json")

    parser.add_argument("--league_spreadsheet_input_path", "-l", required=False,
                        default="content/Mixed-14 Fantasy Football League.xlsx")
    parser.add_argument("--league_spreadsheet_output_path", "-o", required=False,
                        default="output/Mixed-14 Fantasy Football League.xlsx")
    parser.add_argument("--config_path", "-c", required=False,
                        default="content/14_team_config.json")
    args = parser.parse_args()

    # SCHEDULE_PATH = Path(args.schedule_path).resolve()
    # OUTPUT_PATH = Path(args.output_path).resolve()

    # # create the output directory if it doesn't already exist
    # OUTPUT_PATH.parent.mkdir(exist_ok=True)

    fantasy_football(**vars(args))