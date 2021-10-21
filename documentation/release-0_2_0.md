# <a name="release2"></a>Release 0.2.0 - 2021-09-27

This is the last release that contains the 3 script files for separate functions: `schedule_json_generator.py`, `generate_schedule_xlsx.py`, and `run_league_update.py`. Starting in release `0.3.0`, all of these are maintained as wrapper operations in `fantasy_football.py`. (They no longer need to be managed individually, as `fantasy_football.py` handles it all with grace!)

For those using the legacy `0.2.0` version, here is the information that was removed from the README during the release of `0.3.0`.

## Configure the Schedule JSON

Once you've established connections to the ESPN API, it's time to start building the schedule. (Note, a sample "league spreadsheet" will be provided later and stored in the `content` directory.) In the `content` directory, there is a random 14-team league schedule. It's crude, but it was enough to parse to not have to manually create a schedule for 13 weeks (each team plays every other team _once_).

To generate the schedule as a .json file, simply run `python schedule_json_generator.py`.

## Generate the Schedule

Once you have `schedule.json` in the `outputs` directory, you're ready to populate the schedule in the master spreadsheet (sample provided later). Once the spreadsheet is in the `content` directory (it is _not_ part of the commits for privacy reasons), simply run `python generate_schedule_xlsx.py`. This is also a handy way to [reset team names](#reset_teams).

## Update the Spreadsheet (as much as you want!)

Once the spreadsheet is loaded with the schedule, you're basically only going to be calling one script from now on. That script is run by running `python run_league_update.py`. The only time you might need to run something else is if someone changes their team name. Sadly, the schedule will be off and everything will crash. In that case, simply [reset the team names](#reset_teams) and then run `python run_league_update.py` again.

## <a name="reset_teams"></a>Reset Team Names

Teams change, people's attitudes toward FF change, and teams' names change throughout the season. This is all part of the FF journey. However, this wreaks havoc on this script, as there becomes a discrepancy between the schedule on the master spreadsheet and the team name in ESPN. Bummer.

Fortunately, simply re-running `python generate_schedule_xlsx.py` simply overwrites like... everything! You might be thinking... but... it's week 12 - we can't erase everything!! **Wrong**. After resetting everything with `generate_schedule.xlsx`, you simply re-run `python run_league_update.py` and, though it might take some seconds, the league updater script should go through, tediously and tirelessly week-by-week, and update all tabs, scores, records, and the current lineup. It's that easy.