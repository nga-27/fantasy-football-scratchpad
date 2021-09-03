import os
import json
import re
import PyPDF2

from libs.str_utils import split_string, substring_to_lists

SCHEDULE_PATH = os.path.join('content', 'league_schedule_14_team.pdf')
OUTPUT_PATH = os.path.join('output', 'schedule.json')


def generate_schedule():
    if not os.path.exists('output'):
        os.mkdir('output')

    pdf_file_obj = open(SCHEDULE_PATH, 'rb')
    pdf_reader = PyPDF2.PdfFileReader(pdf_file_obj)

    page_obj = pdf_reader.getPage(0)
    pdf_data = page_obj.extractText()
    lines = pdf_data.split("\n")

    schedule = {"weeks": {}}
    schedule["weeks"] = {str(i+1): {} for i in range(13)}

    # Start by fixing line 0...
    cleaned_line0 = lines[0].split('r ')[1].strip()

    week = cleaned_line0[0]
    cleaned_line0 = cleaned_line0.replace(cleaned_line0[0], '', 1)
    game_sets = split_string(cleaned_line0)
    schedule["weeks"][week] = substring_to_lists(game_sets)

    for i in range(1,13):
        line = lines[i].strip()
        if i < 9:
            week = line[0]
            line = line.replace(line[0], '', 1)
        else:
            week = line[0:2]
            line = line.replace(line[0:2], '', 1)
        game_sets = split_string(line)
        schedule["weeks"][week] = substring_to_lists(game_sets)

    with open(os.path.join(OUTPUT_PATH), 'w') as json_f:
        json.dump(schedule, json_f)

generate_schedule()
