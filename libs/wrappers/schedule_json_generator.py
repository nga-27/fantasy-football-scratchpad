"""schedule_json_generator

Generator of schedule.json file
"""
import json
from pathlib import Path


def generate_schedule(schedule_path: Path, output_path: Path):
    """generate_schedule

    Convert the text schedule file to json

    Args:
        schedule_path (Path): raw text path of scheduling
        output_path (Path): path for where the output file would go
    """
    schedule = {"weeks": {}}

    with schedule_path.open('r') as input_file:
        for i, line in enumerate(input_file.read().splitlines()):
            matchups = [matchup.split("-") for matchup in line.split()]
            schedule["weeks"][str(i + 1)] = matchups

    with output_path.open('w') as json_f:
        json.dump(schedule, json_f)
