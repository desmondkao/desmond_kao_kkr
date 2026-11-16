# capacity_dwell1

A fixed arrival rate can't be compared across buildings: 0.8 passengers per
tick swamps 2 cars in 30 floors but barely loads 8. So, for each building:

1. Handling capacity: the highest arrival rate each dispatcher sustains before
   its queue grows (found by bisection). This is the number elevator
   engineers size buildings by.
2. Trip times at half of that building's capacity (the best capacity any
   dispatcher reached), so every building is equally busy.

Dwell 1. Capacity in passengers per tick (3 seeds x 1200 ticks per test).

| building | scenario | round-robin | nearest | directional | zone | etd | ETD vs best other |
|---|---|---|---|---|---|---|---|
| 10 floors, 4 cars | up-peak | 1.80 | 1.62 | 1.78 | 2.46 | 2.00 | -19% |
| 10 floors, 4 cars | lunch | 2.86 | 2.46 | 2.82 | 3.30 | 3.43 | +4% |
| 30 floors, 2 cars | up-peak | 0.32 | 0.31 | 0.28 | 0.45 | 0.36 | -21% |
| 30 floors, 2 cars | lunch | 0.63 | 0.64 | 0.58 | 0.66 | 0.67 | +1% |
| 30 floors, 4 cars | up-peak | 0.72 | 0.66 | 0.64 | 0.95 | 0.74 | -22% |
| 30 floors, 4 cars | lunch | 1.19 | 1.14 | 1.08 | 1.33 | 1.40 | +5% |
| 30 floors, 8 cars | up-peak | 1.49 | 0.88 | 0.71 | 1.73 | 1.60 | -8% |
| 30 floors, 8 cars | lunch | 2.26 | 1.75 | 1.40 | 2.67 | 2.74 | +3% |
| 60 floors, 4 cars | up-peak | 0.43 | 0.04 | 0.24 | 0.51 | 0.44 | -13% |
| 60 floors, 4 cars | lunch | 0.70 | 0.63 | 0.65 | 0.80 | 0.76 | -4% |
| 60 floors, 8 cars | up-peak | 0.81 | 0.04 | 0.46 | 1.11 | 0.82 | -26% |
| 60 floors, 8 cars | lunch | 1.39 | 1.30 | 1.23 | 1.55 | 1.51 | -3% |

Mean total time in ticks at half of the building's capacity (10 seeds x 1200 ticks, ± 95% CI).

| building | scenario | arrivals | round-robin | nearest | directional | zone | etd |
|---|---|---|---|---|---|---|---|
| 10 floors, 4 cars | up-peak | 1.23/tick | 18.5 ±0.1 | 32.2 ±4.1 | 16.9 ±0.6 | 13.7 ±0.1 | **11.7** ±0.1 |
| 10 floors, 4 cars | lunch | 1.71/tick | 20.5 ±0.2 | 20.3 ±0.6 | 15.3 ±0.5 | 14.8 ±0.2 | **11.9** ±0.1 |
| 30 floors, 2 cars | up-peak | 0.23/tick | 45.9 ±0.6 | 47.9 ±2.6 | 36.9 ±1.2 | 39.0 ±0.8 | **35.2** ±1.2 |
| 30 floors, 2 cars | lunch | 0.34/tick | 50.7 ±0.6 | 50.4 ±0.8 | 43.5 ±2.0 | 44.3 ±0.9 | **40.8** ±1.2 |
| 30 floors, 4 cars | up-peak | 0.48/tick | 46.4 ±0.4 | 56.4 ±5.7 | 40.6 ±2.3 | 38.2 ±0.6 | **31.1** ±0.5 |
| 30 floors, 4 cars | lunch | 0.70/tick | 50.5 ±0.3 | 50.4 ±1.0 | 38.3 ±2.6 | 41.3 ±0.6 | **31.6** ±1.0 |
| 30 floors, 8 cars | up-peak | 0.87/tick | 45.3 ±0.3 | 66.3 ±7.4 | 53.1 ±5.0 | 35.1 ±0.7 | **29.4** ±0.4 |
| 30 floors, 8 cars | lunch | 1.37/tick | 50.0 ±0.4 | 47.7 ±0.8 | 32.1 ±0.8 | 38.3 ±0.4 | **25.0** ±0.4 |
| 60 floors, 4 cars | up-peak | 0.26/tick | 86.8 ±1.4 | 102.7 ±12.1 | 76.1 ±6.6 | 71.8 ±2.2 | **59.1** ±1.3 |
| 60 floors, 4 cars | lunch | 0.40/tick | 94.3 ±0.8 | 97.2 ±2.2 | 75.9 ±6.0 | 80.2 ±1.7 | **60.1** ±2.5 |
| 60 floors, 8 cars | up-peak | 0.55/tick | 88.1 ±0.7 | 150.3 ±27.2 | 120.0 ±14.8 | 71.3 ±1.8 | **61.8** ±1.6 |
| 60 floors, 8 cars | lunch | 0.78/tick | 92.8 ±1.0 | 94.4 ±4.1 | 65.4 ±3.1 | 75.4 ±0.9 | **46.7** ±0.7 |
