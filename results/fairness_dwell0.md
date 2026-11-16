# fairness_dwell0

How does ETD's cost exponent trade average time against the worst case?

10 seeds x 1200 ticks of arrivals. Times in ticks.

| building | scenario | rate | dispatcher | wait_mean | total_mean | total_ci95 | total_p95 | total_max | vs_ideal |
|---|---|---|---|---|---|---|---|---|---|
| standard | up-peak | 0.8 | etd-p1 | 18.9 | 33.3 | ±0.9 | 54.8 | 75.4 | 2.31 |
| standard | up-peak | 0.8 | etd-p2 | 18.9 | 33.3 | ±1.0 | 54.7 | 71.2 | 2.31 |
| standard | up-peak | 0.8 | etd-p4 | 18.4 | 32.8 | ±0.9 | 53.8 | 69.2 | 2.28 |
| standard | down-peak | 0.8 | etd-p1 | 11.5 | 26.0 | ±0.5 | 51.8 | 80.1 | 1.80 |
| standard | down-peak | 0.8 | etd-p2 | 11.6 | 26.0 | ±0.5 | 52.1 | 77.5 | 1.80 |
| standard | down-peak | 0.8 | etd-p4 | 11.2 | 25.7 | ±0.4 | 50.3 | 69.5 | 1.78 |
| standard | lunch | 0.8 | etd-p1 | 8.8 | 23.4 | ±0.4 | 42.6 | 63.9 | 1.60 |
| standard | lunch | 0.8 | etd-p2 | 9.0 | 23.6 | ±0.6 | 43.4 | 63.7 | 1.62 |
| standard | lunch | 0.8 | etd-p4 | 8.8 | 23.4 | ±0.4 | 43.0 | 63.3 | 1.60 |
| standard | interfloor | 0.8 | etd-p1 | 8.4 | 18.4 | ±0.2 | 36.1 | 58.9 | 1.83 |
| standard | interfloor | 0.8 | etd-p2 | 8.3 | 18.4 | ±0.3 | 35.7 | 54.8 | 1.83 |
| standard | interfloor | 0.8 | etd-p4 | 8.8 | 18.8 | ±0.5 | 36.5 | 55.1 | 1.87 |
