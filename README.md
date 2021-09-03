# fantasy-football-scratchpad

I need to manage a fantasy football league with 14 teams. Since 14-team leagues are boring with low scores and having to rely heavily on bench players and games decided by only a few points every week, why not have 2 leagues of 8 (two "robots") that can play across each other?

Answer: ESPN/NFL doesn't allow it, as far as I know.

Solution: this repo. Being commissioner in both leagues, I'm using the [ESPN API](https://github.com/cwendt94/espn-api) to manage a master spreadsheet with all things fantasy football league.

# How to Run

## Configure the API

You'll need a few configuration things first.

1) Copy-paste your own copy of `.env.example` and save it as `.env`. 
2) You'll need to fill out the keys in the `.env` file. `ESPN_SWID` and `ESPN_S2` are found by [inspecting the ESPN site](https://github.com/cwendt94/espn-api/discussions/150). 
3) The other keys are found by one's own league sites. Note, since I'm managing two leagues simultaneously (i.e. the point of this repo), I have two keys for league IDs. I randomly named them "regions" of NE and SW. You can have w/e you want, but for this work, keep the key names as they are.

Once you have these pieces, it's a good time to run `python explore_api.py`. This will ensure you have proper connection to the ESPN API.

## Configure the Schedule JSON

Once you've established connections to the ESPN API, it's time to start building the schedule. (Note, a sample "league spreadsheet" will be provided later and stored in the `content` directory.) In the `content` directory, there is a random 14-team league schedule for... billiards. It's crude, and it's a PDF, but it was enough to parse to not have to manually create a schedule for 13 weeks (each team plays every other team _once_). I will admit that there is a typo in the PDF that causes a weird bug in the week 13 matchups, but just go ahead and fix that manually, and you should be good.

To generate the schedule as a .json file (way easier than a gross PDF), simply run `python pdf_to_json.py`. Again, you'll have to fix Week 13 in the JSON file, but that's pretty minimal. (Use the PDF as reference to what the fixed matchup should be, if needed.)

## Generate the Schedule

Once you have `schedule.json` in the `outputs` directory, you're ready to populate the schedule in the master spreadsheet (sample provided later). Once the spreadsheet is in the `content` directory (it is _not_ part of the commits for privacy reasons), simply run `python generate_schedule_xlsx.py`. This is also a handy way to [reset team names](#reset_teams).

## Update the Spreadsheet (as much as you want!)

Once the spreadsheet is loaded with the schedule, you're basically only going to be calling one script from now on. That script is run by running `python run_league_update.py`. The only time you might need to run something else is if someone changes their team name. Sadly, the schedule will be off and everything will crash. In that case, simply [reset the team names](#reset_teams) and then run `python run_league_update.py` again.

## <a name="reset_teams"></a>Reset Team Names

Teams change, people's attitudes toward FF change, and teams' names change throughout the season. This is all part of the FF journey. However, this wreaks havoc on this script, as there becomes a discrepancy between the schedule on the master spreadsheet and the team name in ESPN. Bummer.

Fortunately, simply re-running `python generate_schedule_xlsx.py` simply overwrites like... everything! You might be thinking... but... it's week 12 - we can't erase everything!! **Wrong**. After resetting everything with `generate_schedule.xlsx`, you simply re-run `python run_league_update.py` and, though it might take some seconds, the league updater script should go through, tediously and tirelessly week-by-week, and update all tabs, scores, records, and the current lineup. It's that easy.
