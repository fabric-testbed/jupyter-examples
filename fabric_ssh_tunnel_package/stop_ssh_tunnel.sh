#!/bin/sh

DIR=$(dirname "$0")

PID_DIR='tunnel_pids'

#cd ${DIR}

for pid_file in "$@"; do
   if [ -f "$pid_file" ]; then
      echo kill ${pid_file}

      kill $(cat ${pid_file})
      rm ${pid_file}
 
   else
      echo not killing $pid_file
   fi
done




