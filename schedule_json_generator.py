import json
import argparse
from pathlib import Path


def generate_schedule(schedule_path: Path, output_path: Path):
    schedule = {"weeks": {}}

    with schedule_path.open('r') as inputFile:
        for i, line in enumerate(inputFile.read().splitlines()):
            matchups = [[matchup.split("-")[0], matchup.split("-")[1]] for matchup in line.split()]
            schedule["weeks"][str(i + 1)] = matchups

    with output_path.open('w') as json_f:
        json.dump(schedule, json_f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Generate the JSON version of the schedule")
    parser.add_argument("--schedule_path", "-s", required=False, default="content/14_team_league_schedule.txt")
    parser.add_argument("--output_path", "-o", required=False, default="output/schedule.json")
    args = parser.parse_args()

    SCHEDULE_PATH = Path(args.schedule_path).resolve()
    OUTPUT_PATH = Path(args.output_path).resolve()

    # create the output directory if it doesn't already exist
    OUTPUT_PATH.parent.mkdir(exist_ok=True)

    generate_schedule(SCHEDULE_PATH, OUTPUT_PATH)
