# algorithms_dwell1

Which dispatcher works best?

10 seeds x 1200 ticks of arrivals. Times in ticks.

| building | scenario | rate | dispatcher | wait_mean | total_mean | total_ci95 | total_p95 | total_max | vs_ideal |
|---|---|---|---|---|---|---|---|---|---|
| standard | up-peak | 0.4 | round-robin | 27.2 | 44.6 | ±0.6 | 77.6 | 93.8 | 3.08 |
| standard | up-peak | 0.4 | nearest | 32.4 | 50.7 | ±2.7 | 107.9 | 171.6 | 3.51 |
| standard | up-peak | 0.4 | directional | 16.7 | 35.3 | ±1.5 | 84.4 | 117.6 | 2.44 |
| standard | up-peak | 0.4 | zone | 20.0 | 36.6 | ±0.7 | 76.8 | 95.4 | 2.53 |
| standard | up-peak | 0.4 | etd | 12.1 | 30.2 | ±0.6 | 51.8 | 63.7 | 2.09 |
| standard | up-peak | 0.8 | round-robin | 102.3 | 121.3 | ±11.5 | 230.9 | 285.4 | 8.44 |
| standard | up-peak | 0.8 | nearest | 158.9 | 177.9 | ±23.8 | 494.8 | 604.1 | 12.38 |
| standard | up-peak | 0.8 | directional | 144.3 | 163.3 | ±16.0 | 477.9 | 640.1 | 11.35 |
| standard | up-peak | 0.8 | zone | 40.7 | 58.1 | ±3.5 | 157.9 | 224.5 | 4.03 |
| standard | up-peak | 0.8 | etd | 66.1 | 84.9 | ±7.9 | 150.4 | 180.2 | 5.91 |
| standard | down-peak | 0.4 | round-robin | 27.1 | 44.5 | ±0.4 | 79.0 | 95.5 | 3.08 |
| standard | down-peak | 0.4 | nearest | 31.9 | 49.7 | ±3.2 | 118.0 | 232.9 | 3.44 |
| standard | down-peak | 0.4 | directional | 14.5 | 32.0 | ±0.7 | 63.8 | 107.3 | 2.21 |
| standard | down-peak | 0.4 | zone | 20.8 | 37.6 | ±0.5 | 78.2 | 100.1 | 2.60 |
| standard | down-peak | 0.4 | etd | 12.8 | 29.7 | ±0.4 | 59.8 | 77.1 | 2.05 |
| standard | down-peak | 0.8 | round-robin | 58.7 | 77.1 | ±1.9 | 174.2 | 281.7 | 5.36 |
| standard | down-peak | 0.8 | nearest | 62.6 | 80.9 | ±3.5 | 214.1 | 355.5 | 5.62 |
| standard | down-peak | 0.8 | directional | 44.9 | 63.2 | ±2.9 | 169.5 | 278.7 | 4.39 |
| standard | down-peak | 0.8 | zone | 50.6 | 67.8 | ±3.7 | 223.2 | 361.9 | 4.70 |
| standard | down-peak | 0.8 | etd | 18.1 | 36.0 | ±1.0 | 67.9 | 99.9 | 2.50 |
| standard | lunch | 0.4 | round-robin | 28.0 | 44.8 | ±0.6 | 77.9 | 95.3 | 3.07 |
| standard | lunch | 0.4 | nearest | 23.0 | 40.2 | ±1.0 | 84.4 | 104.0 | 2.76 |
| standard | lunch | 0.4 | directional | 10.7 | 27.9 | ±0.7 | 56.5 | 88.6 | 1.91 |
| standard | lunch | 0.4 | zone | 20.2 | 36.7 | ±0.4 | 76.5 | 94.9 | 2.52 |
| standard | lunch | 0.4 | etd | 9.5 | 26.3 | ±0.6 | 47.7 | 68.3 | 1.80 |
| standard | lunch | 0.8 | round-robin | 34.2 | 52.7 | ±0.6 | 90.6 | 129.4 | 3.61 |
| standard | lunch | 0.8 | nearest | 37.9 | 56.7 | ±1.9 | 114.6 | 261.4 | 3.88 |
| standard | lunch | 0.8 | directional | 30.6 | 49.5 | ±3.8 | 119.0 | 225.0 | 3.39 |
| standard | lunch | 0.8 | zone | 25.5 | 42.9 | ±0.7 | 83.5 | 158.4 | 2.93 |
| standard | lunch | 0.8 | etd | 14.9 | 33.2 | ±0.6 | 59.1 | 87.0 | 2.27 |
| standard | interfloor | 0.4 | round-robin | 28.3 | 40.8 | ±0.8 | 73.2 | 91.6 | 4.07 |
| standard | interfloor | 0.4 | nearest | 23.6 | 36.5 | ±0.7 | 80.4 | 104.0 | 3.65 |
| standard | interfloor | 0.4 | directional | 12.5 | 25.3 | ±0.6 | 56.5 | 89.2 | 2.52 |
| standard | interfloor | 0.4 | zone | 25.8 | 39.1 | ±1.2 | 73.8 | 110.0 | 3.90 |
| standard | interfloor | 0.4 | etd | 11.3 | 23.7 | ±0.8 | 45.1 | 64.0 | 2.36 |
| standard | interfloor | 0.8 | round-robin | 37.1 | 51.7 | ±0.7 | 91.6 | 114.3 | 5.15 |
| standard | interfloor | 0.8 | nearest | 33.0 | 48.0 | ±1.0 | 101.8 | 180.7 | 4.78 |
| standard | interfloor | 0.8 | directional | 23.8 | 38.9 | ±2.0 | 82.6 | 164.4 | 3.87 |
| standard | interfloor | 0.8 | zone | 70.0 | 84.7 | ±3.8 | 248.3 | 402.7 | 8.44 |
| standard | interfloor | 0.8 | etd | 16.0 | 30.1 | ±0.8 | 56.2 | 91.3 | 2.99 |
