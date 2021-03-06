"""explore_api.py

Simple "get an understanding" of the ESPN API
"""

import pprint
from espn_api.football import League

from libs.config import CONFIG_SETTINGS

pprint.pprint(CONFIG_SETTINGS)

NE_LEAGUE = League(
    league_id=CONFIG_SETTINGS["league_id_ne"],
    year=CONFIG_SETTINGS["year"],
    espn_s2=CONFIG_SETTINGS["espn_s2"],
    swid=CONFIG_SETTINGS["swid"]
)

SW_LEAGUE = League(
    league_id=CONFIG_SETTINGS["league_id_sw"],
    year=CONFIG_SETTINGS["year"],
    espn_s2=CONFIG_SETTINGS["espn_s2"],
    swid=CONFIG_SETTINGS["swid"]
)

print("")
print(f"NE League: {NE_LEAGUE}")
print(f"Teams: {NE_LEAGUE.teams}")

print("")
print(f"SW League: {SW_LEAGUE}")
print(f"Teams: {SW_LEAGUE.teams}")

print("")
print(NE_LEAGUE.box_scores(2)[0])
print(NE_LEAGUE.box_scores(2)[0].home_lineup)

print("")
# This could be how we determine the "Inverse Managerial Index"
for player in NE_LEAGUE.box_scores(2)[0].home_lineup:
    print(player.position, player.slot_position, player.eligibleSlots, player)
