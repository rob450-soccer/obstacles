#!/bin/bash
set -u
child_pids=()

cleanup_done=0
cleanup() {
  if [[ "$cleanup_done" -eq 1 ]]; then return; fi
  cleanup_done=1
  [[ "${#child_pids[@]}" -eq 0 ]] && return
  echo "Shutting down obstacle processes..."
  kill -TERM "${child_pids[@]}" 2>/dev/null || true
  for _ in {1..20}; do
    any_alive=0
    for pid in "${child_pids[@]}"; do
      kill -0 "$pid" 2>/dev/null && any_alive=1 && break
    done
    [[ "$any_alive" -eq 0 ]] && break
    sleep 0.1
  done
  kill -KILL "${child_pids[@]}" 2>/dev/null || true
}
trap cleanup INT TERM EXIT

echo "Executing: python3 run_obstacles.py --number 1 --x 1.00 --y 0.25"
python3 run_obstacles.py --number 1 --x 1.00 --y 0.25 &
child_pids+=($!)

echo "Executing: python3 run_obstacles.py --number 2 --x 1.00 --y -0.25"
python3 run_obstacles.py --number 2 --x 1.00 --y -0.25 &
child_pids+=($!)

echo "Executing: python3 run_obstacles.py --number 3 --x 4.50 --y 2.00"
python3 run_obstacles.py --number 3 --x 4.50 --y 2.00 &
child_pids+=($!)

wait "${child_pids[@]}"