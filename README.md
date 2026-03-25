# Obstacles

Minimal robot connection to the server: robots will not move, merely exist.

```
python3 run_obstacles.py --number 1 --x 5.0 --y 2.0
```

Run multiple obstacle robots by starting the script multiple times with different `--number` and poses.

There are some more command line arguments but the defaults should be fine.

Note that negative x will not work as the side of the field at setup is constrained to the team's side, which depends on which team joins the simulation first. 
