#! /bin/sh
source .env

# Active time stop times (when a script should stop for the [night])
echo "Stop time: $CRON_END_TIME"

current=$(date +%H:%M:%S)
while [[ $current < $CRON_END_TIME ]]
do
    python fantasy_football.py

    sleep 2
    echo "Copying updated league..."
    
    python copier.py
    echo "Done." 
    sleep $CRON_FREQUENCY_SEC
    current=$(date +%H:%M:%S)
done