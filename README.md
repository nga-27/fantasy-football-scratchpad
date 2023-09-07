# fantasy-football-scratchpad

I need to manage a fantasy football league with 14 teams. Since 14-team leagues are boring with low scores and having to rely heavily on bench players and games decided by only a few points every week, why not have 2 leagues of 8 (two "robots") that can play across each other?

Answer: ESPN/NFL doesn't allow it, as far as I know.

Solution: this repo. Being commissioner in both leagues, I'm using the [ESPN API](https://github.com/cwendt94/espn-api) to manage a master spreadsheet with all things fantasy football league.

# How to Run

## <a name="configuration"></a>Configure the [API](https://github.com/cwendt94/espn-api/wiki/Football-Intro)

First, a huge shout out to [cwendt94](https://github.com/cwendt94) for making this possible with his wrapped APIs, above.

You'll need a few configuration things first.

1) Copy-paste your own copy of `.env.example` and save it as `.env`. 
2) You'll need to fill out the keys in the `.env` file. `ESPN_SWID` and `ESPN_S2` are found by [inspecting the ESPN site](https://github.com/cwendt94/espn-api/discussions/150). You optionally will have the opportunity to set the playing and bench position your league offers.
3) The other keys are found by one's own league sites. Note, since I'm managing two leagues simultaneously (i.e. the point of this repo), I have two keys for league IDs. I randomly named them "regions" of NE and SW. You can have w/e you want, but for this work, keep the key names as they are.
4) **Optional**- if planning to use the `ff_job.sh` shell script to have it run every 5ish minutes until 11:45pm (local time), then you'll want to fill out `SHARE_DIRECTORY_PATH` and `INPUT_SOURCE_PATH`. ["Cron" script](#cron)

Once you have these pieces, it's a good time to run `python explore_api.py`. This will ensure you have proper connection to the ESPN API.

## Simplicity in Release 0.3.0+ (`fantasy_football.py`)

Starting in release `0.3.0`, the separate managing scripts became high-level wrapper functions. In their place, the function `fantasy_football.py` handles all repo-based functionality. (The documentation for the "old" way is still [here](documentation/release-0_2_0.md#Release2), but deprecated.) That all being said, `0.3.0` and beyond is **not backward compatible**, meaning if you want to run an individual script for reasons unknown, you have to revert your branch back to the `0.2.0` release and then run them.

### Why One Script to Rule Them All?

Once the repo is configured [above](#configuration), there's not really any reason to use scripts `schedule_json_generator.py` and `generate_schedule_xlsx.py`. The maintainer of the league really will only use `run_league_update.py`. There is a caveat, however:

_If someone in your league changes their team name, then you need to ["reset"](documentation/release-0_2_0#reset_teams) the league before running `run_league_update`._

Normally, this wouldn't be a huge issue. However, in my first year doing this, a player loved to spite everyone they played by changing their team's name to mock their opponent. (As I write this, this person is in first place, so I _guess_ the annoyance is merited?) Anyway, it was annoying to have to continually reset the league every Tuesday or Wednesday, so I decided to make a single script to solve the league.

## Running the Single Script `fantasy_football.py`

This single script operates by first evaluating if the schedule json file exists. If it does, it then tries to update the league using the `run_league_update.py` wrapper function. If that fails due the situation outlined above, it re-runs the `generate_schedule_xlsx.py` script to "reset" the league before retrying `run_league_update.py`. All of this conditional updating can be run with one single script call:

```bash
python fantasy_football.py
```

And that's it! You don't need to worry about running scripts in a particular order or if you need to reset the league or not first. About time this came about, right?

## "DB" Functionality in 0.4.0+

Starting in `0.4.0`, a pseudo-DB `db.json` file is employed to help ease the speed of regenerating the league spreadsheet. (Note, that as of 0.4.2, this is not fully realized or optimized yet, though the functionality of the db is utilized.) This is done automatically behind the scenes, so there isn't anything additional that is needed to be done.

The db functionality is designed to only update scores and projected scores of weeks and games that are of the current week. In the event that a past game from a past week needs to be updated to the correct score, currently there is one option: reset the db. This is accomplished by passing the `-d` flag to the script call, as shown below:

```bash
python fantasy_football.py -d 
```

## `0.6.0` Updates

Additionally, starting with `0.6.0+`, you may pass the `-r` arg to the main script. This will force a full reset of the data structures, which includes the DB. The full restart can allow for updated match-ups and a deeper reset of the league. This can be done as below:

```bash
python fantasy_football.py -r
```

Since the list of input parameters has grown [again], another parameter `-p` has been added to print out the other parameters can be utilized to in this app. This will not actually update the fantasy football data, but it will print the other available options in the terminal window.

```bash
python fantasy_football.py -p
```

***Run the above command when a "week" has ended (Tuesday morning) to correct the past weeks' scoring.***

## <a name="cron"></a>"Cron Job" Functionality in 0.5.0+

As alluded to above, version `0.5.0+` features a script `ff_job.sh` that simulates a cron job. Essentially, every 5ish minutes, the python script that runs the league (`fantasy_football.py`) will run. An additional `copier.py` script will run to copy the output of first script to a destination of choice. This is especially handy if you share the league spreadsheet with your league mates in OneDrive or GoogleDrive. (GoogleDrive now has a desktop version that makes this pretty seamless!)

Two values, `CRON_FREQUENCY_SEC` and `CRON_END_TIME`, provide default values in `.env.example`. Feel free to change these as you see fit. Default is 300 seconds and 11:45pm local time, respectively. (Sorry east-coasters... late games that track past midnight for you become complex.)

To run this, you will probably have to allow execution of the shell script. Do this by `chmod +x ff_job.sh`. Then on game day, simply run `./ff_job.sh` and walk away! It'll stop periodically updating and copying the output file at the prescribed stop time that night.

[More details and development to occur in future releases.]
