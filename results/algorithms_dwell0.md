# algorithms_dwell0

Which dispatcher works best?

10 seeds x 1200 ticks of arrivals. Times in ticks. `drift` = how much slower the last third of passengers were than the first third; a large drift means the queue is growing (overloaded).

| building | scenario | rate | dispatcher | wait_mean | total_mean | total_ci95 | total_p95 | total_max | drift | vs_ideal |
|---|---|---|---|---|---|---|---|---|---|---|
| standard | up-peak | 0.4 | round-robin | 24.3 | 38.7 | ±0.4 | 67.9 | 82.7 | 1.7 | 2.68 |
| standard | up-peak | 0.4 | nearest | 25.7 | 40.2 | ±1.4 | 78.7 | 115.2 | 4.2 | 2.78 |
| standard | up-peak | 0.4 | directional | 14.2 | 28.6 | ±0.9 | 61.0 | 92.2 | 2.2 | 1.98 |
| standard | up-peak | 0.4 | zone | 18.0 | 32.5 | ±0.5 | 69.1 | 84.9 | 1.2 | 2.25 |
| standard | up-peak | 0.4 | etd | 11.6 | 26.1 | ±0.5 | 45.5 | 56.0 | 1.2 | 1.80 |
| standard | up-peak | 0.8 | round-robin | 32.2 | 46.6 | ±2.1 | 82.8 | 123.3 | 4.6 | 3.24 |
| standard | up-peak | 0.8 | nearest | 80.5 | 94.9 | ±12.6 | 257.2 | 340.4 | 48.3 | 6.61 |
| standard | up-peak | 0.8 | directional | 63.6 | 78.0 | ±5.3 | 212.8 | 289.9 | 44.0 | 5.42 |
| standard | up-peak | 0.8 | zone | 24.6 | 39.0 | ±1.0 | 86.6 | 134.7 | 1.6 | 2.71 |
| standard | up-peak | 0.8 | etd | 18.9 | 33.3 | ±1.0 | 54.7 | 71.2 | 2.9 | 2.31 |
| standard | down-peak | 0.4 | round-robin | 23.8 | 38.3 | ±0.5 | 67.9 | 81.2 | -0.7 | 2.65 |
| standard | down-peak | 0.4 | nearest | 23.8 | 38.2 | ±1.3 | 82.8 | 149.9 | -0.1 | 2.64 |
| standard | down-peak | 0.4 | directional | 12.6 | 27.0 | ±0.5 | 55.4 | 74.7 | 0.3 | 1.87 |
| standard | down-peak | 0.4 | zone | 18.4 | 32.9 | ±0.5 | 70.2 | 89.6 | 1.8 | 2.27 |
| standard | down-peak | 0.4 | etd | 9.8 | 24.3 | ±0.5 | 51.9 | 65.7 | -0.2 | 1.68 |
| standard | down-peak | 0.8 | round-robin | 30.8 | 45.2 | ±0.6 | 85.0 | 145.6 | 1.1 | 3.14 |
| standard | down-peak | 0.8 | nearest | 38.4 | 52.8 | ±1.6 | 139.6 | 257.3 | -3.9 | 3.67 |
| standard | down-peak | 0.8 | directional | 24.5 | 38.9 | ±1.9 | 101.1 | 192.3 | -2.2 | 2.70 |
| standard | down-peak | 0.8 | zone | 37.1 | 51.5 | ±2.4 | 181.1 | 306.8 | 12.8 | 3.57 |
| standard | down-peak | 0.8 | etd | 11.6 | 26.0 | ±0.5 | 52.1 | 77.5 | 0.4 | 1.80 |
| standard | lunch | 0.4 | round-robin | 24.4 | 39.0 | ±0.7 | 68.8 | 82.6 | 0.0 | 2.67 |
| standard | lunch | 0.4 | nearest | 20.0 | 34.6 | ±0.9 | 72.9 | 84.8 | -0.4 | 2.37 |
| standard | lunch | 0.4 | directional | 8.8 | 23.4 | ±0.3 | 47.5 | 79.5 | 0.3 | 1.61 |
| standard | lunch | 0.4 | zone | 18.0 | 32.6 | ±0.5 | 69.5 | 83.1 | 0.5 | 2.24 |
| standard | lunch | 0.4 | etd | 6.9 | 21.5 | ±0.2 | 39.7 | 56.8 | -0.3 | 1.48 |
| standard | lunch | 0.8 | round-robin | 26.9 | 41.5 | ±0.2 | 71.4 | 85.9 | 0.5 | 2.84 |
| standard | lunch | 0.8 | nearest | 25.2 | 39.9 | ±0.7 | 77.4 | 126.8 | -1.2 | 2.73 |
| standard | lunch | 0.8 | directional | 14.6 | 29.2 | ±1.5 | 66.2 | 130.1 | -0.8 | 2.00 |
| standard | lunch | 0.8 | zone | 20.6 | 35.2 | ±0.6 | 71.6 | 102.9 | 0.2 | 2.41 |
| standard | lunch | 0.8 | etd | 9.0 | 23.6 | ±0.6 | 43.4 | 63.7 | -0.5 | 1.62 |
| standard | interfloor | 0.4 | round-robin | 22.5 | 32.5 | ±0.7 | 58.8 | 73.4 | 0.9 | 3.25 |
| standard | interfloor | 0.4 | nearest | 17.1 | 27.1 | ±0.8 | 60.8 | 77.0 | -0.8 | 2.70 |
| standard | interfloor | 0.4 | directional | 9.3 | 19.3 | ±0.6 | 43.9 | 68.7 | -0.5 | 1.93 |
| standard | interfloor | 0.4 | zone | 20.3 | 30.3 | ±0.9 | 57.5 | 79.3 | -0.7 | 3.02 |
| standard | interfloor | 0.4 | etd | 7.0 | 17.0 | ±0.4 | 33.6 | 50.5 | -0.2 | 1.70 |
| standard | interfloor | 0.8 | round-robin | 25.3 | 35.4 | ±0.3 | 62.3 | 77.3 | 0.5 | 3.52 |
| standard | interfloor | 0.8 | nearest | 21.2 | 31.3 | ±0.6 | 65.8 | 83.4 | -0.1 | 3.11 |
| standard | interfloor | 0.8 | directional | 12.3 | 22.3 | ±0.5 | 50.5 | 75.3 | -0.2 | 2.22 |
| standard | interfloor | 0.8 | zone | 31.2 | 41.3 | ±2.0 | 99.0 | 203.7 | 6.2 | 4.11 |
| standard | interfloor | 0.8 | etd | 8.3 | 18.4 | ±0.3 | 35.7 | 54.8 | 0.5 | 1.83 |
