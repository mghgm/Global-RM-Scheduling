#!/usr/bin/bash

rm -rf out 
mkdir -p out

for i in $(seq 1 24); do
    for j in $(seq 1 100); do
        echo "Config $i Iteration $j"
        python src/p_fmlp.py $i
        if [ $? -eq 1 ]; then
            echo "Missed" >> out/p_fmlp_$i.log
        else 
            echo "Success" >> out/p_fmlp_$i.log
        fi
        python src/p_pip.py $i
        if [ $? -eq 1 ]; then
            echo "Missed" >> out/p_pip_$i.log
        else 
            echo "Success" >> out/p_pip_$i.log
        fi
    done
done
