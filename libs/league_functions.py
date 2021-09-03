import datetime

def load_schedule(xlsx_dict: dict, schedule: dict) -> dict:
    date_now = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    for week in schedule["weeks"]:
        key = f"Week {week}"
        xlsx_dict[key] = {"Team": [], "Score": []}
        xlsx_dict[key]["Team"].append("")
        xlsx_dict[key]["Score"].append("")
        xlsx_dict[key]["Team"].append("Last Updated:")
        xlsx_dict[key]["Score"].append(date_now)
        xlsx_dict[key]["Team"].append("")
        xlsx_dict[key]["Score"].append("")

        for game in schedule["weeks"][week]:
            xlsx_dict[key]["Team"].append(f"Team {game[0]}")
            xlsx_dict[key]["Score"].append(0)
            xlsx_dict[key]["Team"].append(f"Team {game[1]}")
            xlsx_dict[key]["Score"].append(0)
            xlsx_dict[key]["Team"].extend(["", ""])
            xlsx_dict[key]["Score"].extend(["", ""])


    return xlsx_dict