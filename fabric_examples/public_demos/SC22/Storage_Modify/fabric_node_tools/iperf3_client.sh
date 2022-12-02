#!/bin/bash
run_name=$1
shift
target_ip=$1
shift
processes=$1
shift

start_port=5100
file_name=${run_name}
summary_file=${file_name=}_client_summary_output
 
sudo yum install -y -q iperf3 iproute-tc

killall iperf3 > /dev/null 2>&1

for i in $(seq 1 $processes); do 
    echo $i; 
    port=$((start_port + i)) 

    echo iperf3 -c $target_ip -J $@ -p $port --logfile ${file_name}_${port}_output
    iperf3 -c $target_ip -J $@ -p $port --logfile ${file_name}_${port}_output &
    pids[${i}]=$!
    echo pids[${i}]
done


#wait for all pids
for pid in ${pids[*]}; do
    echo wating for pid $pid
    wait $pid
done


echo '[' > $summary_file
for i in $(seq 1 $processes); do
    echo $i;
    port=$((start_port + i))

    if [ $i -eq 1 ]
    then
        cat ${file_name}_${port}_output  >> $summary_file
    else
        echo ',' >> $summary_file
        cat ${file_name}_${port}_output  >> $summary_file
    fi
done
echo ']' >>  $summary_file


echo Done!
