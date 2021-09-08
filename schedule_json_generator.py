import os
import json

SCHEDULE_PATH = os.path.join('content', '14_team_league_schedule.txt')
OUTPUT_PATH = os.path.join('output', 'schedule.json')

def generate_schedule():
    if not os.path.exists('output'):
        os.mkdir('output')

    schedule = {"weeks": {}}
    with open(SCHEDULE_PATH, "r") as inputFile:
        lines = inputFile.read().splitlines()
        for i in range(len(lines)):
            matchups = [[matchup.split("-")[0], matchup.split("-")[1]] for matchup in lines[i].split()]
            schedule["weeks"][str(i+1)] = matchups

    with open(os.path.join(OUTPUT_PATH), 'w') as json_f:
        json.dump(schedule, json_f)

generate_schedule()
