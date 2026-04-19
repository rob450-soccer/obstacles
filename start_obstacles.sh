#!/bin/bash
set -u

# for intial setup screenshot
# python3 run_obstacles.py --number 1 --x 2.5 --y 2.0 &
# python3 run_obstacles.py --number 2 --x 2.5 --y -2.0 &
# python3 run_obstacles.py --number 3 --x 5.5 --y 0.0 &
# exit 0

# Generate random floats using awk
# $RANDOM is passed as a seed so the numbers change even if the loop runs in the same second

child_pids=()
cleanup_done=0

cleanup() {
  if [[ "$cleanup_done" -eq 1 ]]; then
    return
  fi
  cleanup_done=1

  if [[ "${#child_pids[@]}" -eq 0 ]]; then
    return
  fi

  echo "Shutting down obstacle processes..."
  kill -TERM "${child_pids[@]}" 2>/dev/null || true

  # Give children a moment to exit cleanly.
  for _ in {1..20}; do
    any_alive=0
    for pid in "${child_pids[@]}"; do
      if kill -0 "$pid" 2>/dev/null; then
        any_alive=1
        break
      fi
    done
    if [[ "$any_alive" -eq 0 ]]; then
      break
    fi
    sleep 0.1
  done

  # Force-kill stragglers.
  kill -KILL "${child_pids[@]}" 2>/dev/null || true
}

trap cleanup INT TERM EXIT

CUSTOM=/home/arv/rob450/obstacles/start_obstacles_custom.sh
if [[ -f "$CUSTOM" ]]; then
    echo "Using custom obstacle placement..."
    exec "$CUSTOM"
fi

rand_x_1=$(awk -v min=1.0 -v max=4.5 -v seed=$RANDOM 'BEGIN{srand(seed); printf "%.2f", min+rand()*(max-min)}')
rand_y_1=$(awk -v min=0.0 -v max=4.0 -v seed=$RANDOM 'BEGIN{srand(seed); printf "%.2f", min+rand()*(max-min)}')
echo "Executing: python3 run_obstacles.py --number 1 --x $rand_x_1 --y $rand_y_1"
python3 run_obstacles.py --number 1 --x "$rand_x_1" --y "$rand_y_1" &
child_pids+=($!)

rand_x_2=$(awk -v min=1.0 -v max=4.5 -v seed=$RANDOM 'BEGIN{srand(seed); printf "%.2f", min+rand()*(max-min)}')
rand_y_2=$(awk -v min=-4.0 -v max=0.0 -v seed=$RANDOM 'BEGIN{srand(seed); printf "%.2f", min+rand()*(max-min)}')
echo "Executing: python3 run_obstacles.py --number 2 --x $rand_x_2 --y $rand_y_2"
python3 run_obstacles.py --number 2 --x "$rand_x_2" --y "$rand_y_2" &
child_pids+=($!)

rand_x_3=$(awk -v min=4.5 -v max=6.5 -v seed=$RANDOM 'BEGIN{srand(seed); printf "%.2f", min+rand()*(max-min)}')
rand_y_3=$(awk -v min=-2.0 -v max=2.0 -v seed=$RANDOM 'BEGIN{srand(seed); printf "%.2f", min+rand()*(max-min)}')
echo "Executing: python3 run_obstacles.py --number 3 --x $rand_x_3 --y $rand_y_3"
python3 run_obstacles.py --number 3 --x "$rand_x_3" --y "$rand_y_3" &
child_pids+=($!)

wait "${child_pids[@]}"
