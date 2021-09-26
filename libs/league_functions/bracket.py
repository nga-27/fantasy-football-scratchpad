def load_bracket(xlsx_dict: dict, playoff_data: dict) -> dict:
    xlsx_dict["Playoff Bracket"] = {}
    max_len = 0
    for round_key, round_list in playoff_data['bracket'].items():
        xlsx_dict["Playoff Bracket"][round_key] = round_list
        if len(round_list) > max_len:
            max_len = len(round_list)

    # Because this bracket is for aesthetics, each list object will be different lengths. We need to
    # lengthen these until they are the same length.
    for round_key, round_list in xlsx_dict["Playoff Bracket"].items():
        adding_empties = [""] * (max_len - len(round_list))
        xlsx_dict["Playoff Bracket"][round_key].extend(adding_empties)

    return xlsx_dict