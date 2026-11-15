# express_dwell0

Do express cars (2 of 4 serve only the lobby and floors 16-30) help?

10 seeds x 1200 ticks of arrivals. Times in ticks. `drift` = how much slower the last third of passengers were than the first third; a large drift means the queue is growing (overloaded).

| building | scenario | rate | dispatcher | wait_mean | total_mean | total_ci95 | total_p95 | total_max | drift | vs_ideal |
|---|---|---|---|---|---|---|---|---|---|---|
| standard | up-peak | 0.4 | zone | 18.0 | 32.5 | ±0.5 | 69.1 | 84.9 | 1.2 | 2.25 |
| standard | up-peak | 0.4 | etd | 11.6 | 26.1 | ±0.5 | 45.5 | 56.0 | 1.2 | 1.80 |
| standard | up-peak | 0.8 | zone | 24.6 | 39.0 | ±1.0 | 86.6 | 134.7 | 1.6 | 2.71 |
| standard | up-peak | 0.8 | etd | 18.9 | 33.3 | ±1.0 | 54.7 | 71.2 | 2.9 | 2.31 |
| standard | lunch | 0.4 | zone | 18.0 | 32.6 | ±0.5 | 69.5 | 83.1 | 0.5 | 2.24 |
| standard | lunch | 0.4 | etd | 6.9 | 21.5 | ±0.2 | 39.7 | 56.8 | -0.3 | 1.48 |
| standard | lunch | 0.8 | zone | 20.6 | 35.2 | ±0.6 | 71.6 | 102.9 | 0.2 | 2.41 |
| standard | lunch | 0.8 | etd | 9.0 | 23.6 | ±0.6 | 43.4 | 63.7 | -0.5 | 1.62 |
| express | up-peak | 0.4 | zone | 20.1 | 34.6 | ±0.6 | 68.8 | 85.9 | 2.0 | 2.39 |
| express | up-peak | 0.4 | etd | 13.4 | 27.9 | ±0.5 | 47.5 | 59.2 | 0.5 | 1.93 |
| express | up-peak | 0.8 | zone | 84.7 | 99.1 | ±14.3 | 264.5 | 297.3 | 83.7 | 6.91 |
| express | up-peak | 0.8 | etd | 20.1 | 34.5 | ±0.7 | 54.9 | 77.5 | 0.2 | 2.40 |
| express | lunch | 0.4 | zone | 20.1 | 34.7 | ±0.6 | 70.0 | 84.6 | -0.3 | 2.38 |
| express | lunch | 0.4 | etd | 10.6 | 25.2 | ±0.5 | 44.1 | 61.6 | -0.2 | 1.73 |
| express | lunch | 0.8 | zone | 24.1 | 38.7 | ±0.7 | 73.1 | 118.2 | 0.0 | 2.65 |
| express | lunch | 0.8 | etd | 12.8 | 27.5 | ±0.5 | 47.2 | 71.8 | -0.7 | 1.88 |
