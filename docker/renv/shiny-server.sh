#!/bin/sh

# Make sure the directory for individual app logs exists
mkdir -p /var/log/biovis-report
chown shiny.shiny /var/log/biovis-report

if [ "$APPLICATION_LOGS_TO_STDOUT" != "false" ];
then
    # push the "real" application logs to stdout with xtail in detached mode
    exec xtail /var/log/biovis-report/ &
fi

# start shiny server
exec shiny-server 2>&1