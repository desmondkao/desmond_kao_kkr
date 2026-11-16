# express_dwell1

Do express cars (2 of 4 serve only the lobby and floors 16-30) help?

10 seeds x 1200 ticks of arrivals. Times in ticks.

| building | scenario | rate | dispatcher | wait_mean | total_mean | total_ci95 | total_p95 | total_max | vs_ideal |
|---|---|---|---|---|---|---|---|---|---|
| standard | up-peak | 0.4 | zone | 20.0 | 36.6 | ±0.7 | 76.8 | 95.4 | 2.53 |
| standard | up-peak | 0.4 | etd | 12.1 | 30.2 | ±0.6 | 51.8 | 63.7 | 2.09 |
| standard | up-peak | 0.8 | zone | 40.7 | 58.1 | ±3.5 | 157.9 | 224.5 | 4.03 |
| standard | up-peak | 0.8 | etd | 66.1 | 84.9 | ±7.9 | 150.4 | 180.2 | 5.91 |
| standard | lunch | 0.4 | zone | 20.2 | 36.7 | ±0.4 | 76.5 | 94.9 | 2.52 |
| standard | lunch | 0.4 | etd | 9.5 | 26.3 | ±0.6 | 47.7 | 68.3 | 1.80 |
| standard | lunch | 0.8 | zone | 25.5 | 42.9 | ±0.7 | 83.5 | 158.4 | 2.93 |
| standard | lunch | 0.8 | etd | 14.9 | 33.2 | ±0.6 | 59.1 | 87.0 | 2.27 |
| express | up-peak | 0.4 | zone | 25.2 | 42.5 | ±1.6 | 80.8 | 99.0 | 2.94 |
| express | up-peak | 0.4 | etd | 14.9 | 32.9 | ±0.6 | 54.6 | 68.9 | 2.28 |
| express | up-peak | 0.8 | zone | 191.2 | 209.2 | ±21.4 | 606.6 | 651.7 | 14.56 |
| express | up-peak | 0.8 | etd | 38.2 | 56.7 | ±2.1 | 91.1 | 125.7 | 3.94 |
| express | lunch | 0.4 | zone | 23.6 | 40.6 | ±0.9 | 76.3 | 93.2 | 2.78 |
| express | lunch | 0.4 | etd | 13.5 | 30.5 | ±0.6 | 52.7 | 78.5 | 2.09 |
| express | lunch | 0.8 | zone | 53.6 | 71.5 | ±7.0 | 172.4 | 413.7 | 4.90 |
| express | lunch | 0.8 | etd | 19.8 | 38.0 | ±1.0 | 65.5 | 98.4 | 2.60 |
