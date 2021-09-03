def split_string(line: str) -> list:
    groups = []
    flags = 0
    temp_str = []
    for place in line:
        if flags == 0:
            try:
                int(place)
                flags = 1
                temp_str.append(place)
                continue
            except ValueError:
                continue
        elif flags == 1:
            temp_str.append(place)
            if place == ' ':
                flags = 2
            continue
        elif flags == 2:
            temp_str.append(place)
            if place == '-':
                flags = 3
            continue
        elif flags == 3:
            temp_str.append(place)
            if place == ' ':
                flags = 4
            continue
        elif flags == 4:
            try:
                int(place)
                temp_str.append(place)
                continue
            except ValueError:
                flags = 0
                value = ''.join(temp_str)
                groups.append(value)
                temp_str = []
                continue

    # Last value
    value = ''.join(temp_str)
    groups.append(value)

    return groups


def substring_to_lists(list_of_groups: list) -> list:
    game_list = []
    for substring in list_of_groups:
        teams = substring.split('-')
        game = []
        for team in teams:
            game.append(team.strip())
        game_list.append(game.copy())
    return game_list
