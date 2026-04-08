#!/bin/bash

# for intial setup screenshot
# python3 run_obstacles.py --number 1 --x 2.5 --y 2.0 &
# python3 run_obstacles.py --number 2 --x 2.5 --y -2.0 &
# python3 run_obstacles.py --number 3 --x 5.5 --y 0.0 &
# exit 0

# Generate random floats using awk
# $RANDOM is passed as a seed so the numbers change even if the loop runs in the same second

rand_x_1=$(awk -v min=0.5 -v max=4.5 -v seed=$RANDOM 'BEGIN{srand(seed); printf "%.2f", min+rand()*(max-min)}')
rand_y_1=$(awk -v min=0.0 -v max=4.0 -v seed=$RANDOM 'BEGIN{srand(seed); printf "%.2f", min+rand()*(max-min)}')
echo "Executing: python3 run_obstacles.py --number 1 --x $rand_x_1 --y $rand_y_1"
python3 run_obstacles.py --number 1 --x "$rand_x_1" --y "$rand_y_1" &

rand_x_2=$(awk -v min=0.5 -v max=4.5 -v seed=$RANDOM 'BEGIN{srand(seed); printf "%.2f", min+rand()*(max-min)}')
rand_y_2=$(awk -v min=-4.0 -v max=0.0 -v seed=$RANDOM 'BEGIN{srand(seed); printf "%.2f", min+rand()*(max-min)}')
echo "Executing: python3 run_obstacles.py --number 2 --x $rand_x_2 --y $rand_y_2"
python3 run_obstacles.py --number 2 --x "$rand_x_2" --y "$rand_y_2" &

rand_x_3=$(awk -v min=4.5 -v max=6.5 -v seed=$RANDOM 'BEGIN{srand(seed); printf "%.2f", min+rand()*(max-min)}')
rand_y_3=$(awk -v min=-2.0 -v max=2.0 -v seed=$RANDOM 'BEGIN{srand(seed); printf "%.2f", min+rand()*(max-min)}')
echo "Executing: python3 run_obstacles.py --number 3 --x $rand_x_3 --y $rand_y_3"
python3 run_obstacles.py --number 3 --x "$rand_x_3" --y "$rand_y_3" &
