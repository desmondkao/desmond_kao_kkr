# capacity_dwell0

A fixed arrival rate can't be compared across buildings: 0.8 passengers per
tick swamps 2 cars in 30 floors but barely loads 8. So, for each building:

1. Handling capacity: the highest arrival rate each dispatcher sustains before
   its queue grows (found by bisection). This is the number elevator
   engineers size buildings by.
2. Trip times at half of that building's capacity (the best capacity any
   dispatcher reached), so every building is equally busy.

Dwell 0. Capacity in passengers per tick (3 seeds x 1200 ticks per test).

| building | scenario | round-robin | nearest | directional | zone | etd | ETD vs best other |
|---|---|---|---|---|---|---|---|
| 10 floors, 4 cars | up-peak | 2.74 | 2.14 | 2.60 | 3.30 | 2.78 | -16% |
| 10 floors, 4 cars | lunch | 4.88 | 3.90 | 3.85 | 4.81 | 5.15 | +6% |
| 30 floors, 2 cars | up-peak | 0.47 | 0.29 | 0.46 | 0.49 | 0.48 | -3% |
| 30 floors, 2 cars | lunch | 0.82 | 0.84 | 0.75 | 0.84 | 0.85 | +1% |
| 30 floors, 4 cars | up-peak | 0.86 | 0.74 | 0.74 | 1.21 | 0.88 | -28% |
| 30 floors, 4 cars | lunch | 1.58 | 1.44 | 1.37 | 1.51 | 1.67 | +6% |
| 30 floors, 8 cars | up-peak | 1.78 | 1.58 | 0.72 | 1.73 | 1.80 | +2% |
| 30 floors, 8 cars | lunch | 3.04 | 2.86 | 2.78 | 3.08 | 3.30 | +7% |
| 60 floors, 4 cars | up-peak | 0.47 | 0.05 | 0.23 | 0.52 | 0.49 | -6% |
| 60 floors, 4 cars | lunch | 0.84 | 0.74 | 0.71 | 0.90 | 0.90 | +0% |
| 60 floors, 8 cars | up-peak | 0.90 | 0.64 | 0.23 | 1.15 | 0.90 | -22% |
| 60 floors, 8 cars | lunch | 1.60 | 1.51 | 1.51 | 1.64 | 1.67 | +1% |

Mean total time in ticks at half of the building's capacity (10 seeds x 1200 ticks, ± 95% CI).

| building | scenario | arrivals | round-robin | nearest | directional | zone | etd |
|---|---|---|---|---|---|---|---|
| 10 floors, 4 cars | up-peak | 1.65/tick | 12.7 ±0.1 | 17.2 ±2.7 | 11.9 ±0.4 | 10.8 ±0.1 | **8.8** ±0.1 |
| 10 floors, 4 cars | lunch | 2.58/tick | 13.0 ±0.0 | 11.7 ±0.1 | 8.7 ±0.2 | 11.2 ±0.1 | **7.2** ±0.1 |
| 30 floors, 2 cars | up-peak | 0.25/tick | 39.4 ±0.8 | 42.4 ±2.2 | 30.3 ±1.3 | 34.9 ±0.9 | **28.7** ±0.5 |
| 30 floors, 2 cars | lunch | 0.43/tick | 41.2 ±0.5 | 41.7 ±0.8 | 34.6 ±1.2 | 37.3 ±0.7 | **31.3** ±0.8 |
| 30 floors, 4 cars | up-peak | 0.60/tick | 40.3 ±0.4 | 50.8 ±5.1 | 39.7 ±2.4 | 34.6 ±0.9 | **28.1** ±0.4 |
| 30 floors, 4 cars | lunch | 0.83/tick | 41.3 ±0.3 | 40.3 ±0.9 | 28.2 ±0.9 | 35.3 ±0.4 | **23.4** ±0.4 |
| 30 floors, 8 cars | up-peak | 0.90/tick | 39.2 ±0.5 | 48.9 ±5.0 | 43.9 ±4.0 | 31.8 ±0.5 | **28.9** ±0.6 |
| 30 floors, 8 cars | lunch | 1.65/tick | 41.5 ±0.3 | 38.5 ±0.4 | 24.2 ±0.6 | 34.1 ±0.4 | **18.8** ±0.2 |
| 60 floors, 4 cars | up-peak | 0.26/tick | 79.3 ±1.4 | 95.7 ±11.4 | 65.4 ±4.0 | 66.7 ±1.6 | **54.5** ±0.9 |
| 60 floors, 4 cars | lunch | 0.45/tick | 83.8 ±0.8 | 86.3 ±2.5 | 65.0 ±4.6 | 72.7 ±1.3 | **47.8** ±0.7 |
| 60 floors, 8 cars | up-peak | 0.58/tick | 79.9 ±0.8 | 117.2 ±16.4 | 108.4 ±12.4 | 66.8 ±1.6 | **62.5** ±1.3 |
| 60 floors, 8 cars | lunch | 0.83/tick | 83.4 ±0.6 | 82.4 ±3.5 | 53.1 ±3.5 | 70.0 ±0.9 | **38.9** ±0.3 |
