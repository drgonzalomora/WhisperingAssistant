#!/bin/bash

# This script will check the first argument to see if it's "start" or "stop".
# If it's "start", it will start the alarm in the number of minutes given by the second argument.
# If it's "stop", it will stop the alarm.

SOUND_PATH="/home/joshua/Downloads/powerful-beat-121791.mp3"

if [ "$1" = "start" ]; then
  # Calculate the alarm time
  currentTimeSec=$(date +%s)
  alarmTimeSec=$((currentTimeSec + $2*60))
  alarmTime=$(date -d "@$alarmTimeSec" +%I:%M%p)

  # Wait until the alarm time
  echo "Alarm set for $alarmTime."
  while [ "$(date +%s)" -lt "$alarmTimeSec" ]; do
    sleep 1
  done

  # Loop the alarm sound and store the PID
  while [ ! -f /tmp/alarm_stop ]; do
    ffplay $SOUND_PATH -nodisp -autoexit &
    player_pid=$!
    echo $player_pid > /tmp/alarm_pid
    wait $player_pid
  done

  # Remove the stop file and PID file
  rm /tmp/alarm_stop
  rm /tmp/alarm_pid

elif [ "$1" = "stop" ]; then
  # Create a stop file that the start script can check
  touch /tmp/alarm_stop

  # Get the PID of the sound player
  player_pid=$(cat /tmp/alarm_pid)

  # Kill the sound play command
  kill $player_pid > /dev/null 2>&1
else
  echo "Invalid argument. Please use either \"start\" or \"stop\"."
fi
