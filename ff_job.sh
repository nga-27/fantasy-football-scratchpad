#! /bin/sh

# Active time stop times (when a script should stop for the [night])
end_time=23:45:00
echo "Stop time: $end_time"

current=$(date +%H:%M:%S)
while [[ $current < $end_time ]]
do
    python fantasy_football.py

    sleep 2
    echo "Copying updated league..."
    
    python copier.py
    echo "Done." 
    sleep 300
    current=$(date +%H:%M:%S)
done