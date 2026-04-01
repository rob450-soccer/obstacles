#!/bin/bash

# Loop from 1 to 3
for i in {1..3}; do
    # Generate random floats using awk
    # $RANDOM is passed as a seed so the numbers change even if the loop runs in the same second
    rand_x=$(awk -v min=0.5 -v max=6.5 -v seed=$RANDOM 'BEGIN{srand(seed); printf "%.2f", min+rand()*(max-min)}')
    rand_y=$(awk -v min=-4.0 -v max=4.0 -v seed=$RANDOM 'BEGIN{srand(seed); printf "%.2f", min+rand()*(max-min)}')

    # Print the command being run for visibility (optional)
    echo "Executing: python3 run_obstacles.py --number $i --x $rand_x --y $rand_y"

    # Run the Python script
    python3 run_obstacles.py --number "$i" --x "$rand_x" --y "$rand_y" &
done