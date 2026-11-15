# fairness_dwell1

How does ETD's cost exponent trade average time against the worst case?

10 seeds x 1200 ticks of arrivals. Times in ticks. `drift` = how much slower the last third of passengers were than the first third; a large drift means the queue is growing (overloaded).

| building | scenario | rate | dispatcher | wait_mean | total_mean | total_ci95 | total_p95 | total_max | drift | vs_ideal |
|---|---|---|---|---|---|---|---|---|---|---|
| standard | up-peak | 0.8 | etd-p1 | 70.3 | 89.2 | ±8.8 | 160.0 | 187.6 | 71.6 | 6.21 |
| standard | up-peak | 0.8 | etd-p2 | 66.1 | 84.9 | ±7.9 | 150.4 | 180.2 | 67.1 | 5.91 |
| standard | up-peak | 0.8 | etd-p4 | 59.6 | 78.3 | ±7.9 | 132.4 | 157.9 | 55.6 | 5.45 |
| standard | down-peak | 0.8 | etd-p1 | 17.6 | 35.7 | ±0.8 | 67.9 | 110.7 | 0.1 | 2.47 |
| standard | down-peak | 0.8 | etd-p2 | 18.1 | 36.0 | ±1.0 | 67.9 | 99.9 | -0.1 | 2.50 |
| standard | down-peak | 0.8 | etd-p4 | 19.8 | 37.7 | ±0.5 | 66.6 | 93.0 | 1.9 | 2.61 |
| standard | lunch | 0.8 | etd-p1 | 15.8 | 34.1 | ±0.9 | 63.1 | 91.2 | -0.4 | 2.33 |
| standard | lunch | 0.8 | etd-p2 | 14.9 | 33.2 | ±0.6 | 59.1 | 87.0 | 0.5 | 2.27 |
| standard | lunch | 0.8 | etd-p4 | 16.4 | 34.5 | ±0.7 | 58.4 | 84.0 | 1.3 | 2.36 |
| standard | interfloor | 0.8 | etd-p1 | 16.3 | 30.5 | ±1.1 | 59.3 | 101.4 | 1.9 | 3.04 |
| standard | interfloor | 0.8 | etd-p2 | 16.0 | 30.1 | ±0.8 | 56.2 | 91.3 | 1.5 | 2.99 |
| standard | interfloor | 0.8 | etd-p4 | 18.0 | 32.0 | ±0.7 | 55.5 | 81.2 | 1.1 | 3.19 |
