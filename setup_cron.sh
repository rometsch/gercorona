#!/usr/bin/env bash
# Add a cronjob to check every minute for new simulations.
if (( $# == 0 )); then
        BASEDIR="$PWD"
else
        BASEDIR="$(realpath $1)"
fi
SIMDIR="name"
CRONSTR="0 * * * * cd "$BASEDIR"; ./get_data.py >> data/log.txt"
# add to cron jobs
RES=$(crontab -l | grep -F "$CRONSTR")
if [[ -z "$RES" ]]; then
        TMPFILE="$(mktemp)"
        crontab -l > $TMPFILE
        echo "$CRONSTR" >> $TMPFILE
        crontab $TMPFILE
        rm $TMPFILE
fi