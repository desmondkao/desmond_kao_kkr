# Elevator simulation

A discrete-time simulation of a destination-dispatch elevator system. Each passenger is assigned to a car when they call, and the assignment never changes. Time moves one floor per tick, and the simulation only sees requests whose time has come.

The default scheduler is ETD (estimated time to destination). It gives the lowest average trip time of the four dispatchers I tried, in every traffic pattern, until the building nears full capacity.

Python 3.10+, standard library only. Tests use pytest; the charts script uses matplotlib.

## Running it

```bash
python -m elevator_sim examples/spec_example.csv --floors 60 --cars 2
```

This prints a summary and writes `output/positions.csv` (each car's floor at every tick, from 0), `output/passengers.csv` and `output/summary.json`. The input is `time,id,source,dest`; the header is optional.

Options: `--cars`, `--capacity`, `--dispatcher` (`etd`, `zone`, `nearest`, `round-robin`), `--dwell` (extra ticks per stop, default 0), `--express 2,3:1,16-30` (cars 2 and 3 only stop at floor 1 and floors 16-30), `--start-floor`.

From Python:

```python
from elevator_sim import simulate

result = simulate([(0, "passenger1", 1, 51), (0, "passenger2", 1, 37), (10, "passenger3", 20, 1)],
                  floors=60, num_cars=2, capacity=10)
```

Other commands:

```bash
python -m pytest                    # tests
python -m elevator_sim.benchmark    # experiments -> results/ (about 5 min)
python scripts/charts.py            # charts -> docs/charts/
```

Besides min/mean/max wait and total time, the summary reports total time divided by the ideal (`|dest - source|`, which no scheduler can beat) and drift: how much longer the last third of passengers took than the first third. Large positive drift means the queue is growing.

## Design

Two decisions: **dispatch** picks a car for each new passenger, once (`dispatch.py`); **routing** picks each car's direction, every tick (`routing.py`).

Each tick (`engine.py`): assign new requests → at each car, riders get off, the car picks a direction, and waiting passengers going that way get on → log positions → move. Only `feed.py` holds future requests, so nothing can look ahead.

**ETD.** For each car, simulate its future with and without the new passenger, using the engine's own per-car rules (`rules.py`). The difference is the newcomer's trip time plus the delay they add for everyone already assigned to that car. Pick the smallest. Each passenger costs `total_time²`, so one very long trip counts more than several short ones. On the brief's example, round robin makes passenger3 wait 71 ticks; ETD, 19.

**LOOK routing.** Keep going while there are pickups ahead, otherwise turn around. Riders aboard all share one direction, so they decide it.

**No one waits forever.** LOOK with a capacity limit can pass the same floor indefinitely if the car keeps filling up first (there's a test for this). After `max_wait` ticks (default 3 × floors), a car's oldest waiting passenger becomes its target and gets a reserved seat. Nobody is skipped forever, though under overload several overdue passengers queue behind each other.

## Results

30 floors, 4 cars, capacity 10; 10 seeds × 1200 ticks. Mean total time in ticks at 0.8 passengers per tick:

| Scenario | Round robin | Nearest car | Zone | ETD |
|---|---|---|---|---|
| Up-peak | 46.6 | 94.9 | 39.0 | **33.3** |
| Down-peak | 45.2 | 52.8 | 51.5 | **26.0** |
| Lunch | 41.5 | 39.9 | 35.2 | **23.6** |
| Interfloor | 35.4 | 31.3 | 41.3 | **18.4** |

![dispatchers](docs/charts/algorithms.png)

**Where ETD loses: the morning rush.** When each stop costs a tick, ETD spreads lobby passengers across every car, so every car stops at many floors, and the queue grows (up-peak, dwell 1: ETD 85, zone 58). Making cars 2-3 express to floors 16-30 fixes it (57). The same happens with free stops near saturation (1.0 per tick).

![overload](docs/charts/overload.png)

**Fairness.** With one-tick stops, raising the cost exponent from 1 to 4 cuts the worst trip by 16-20% in every pattern, without making the mean worse.

![fairness](docs/charts/fairness.png)

Full tables are in `results/`; more charts are in `docs/charts/`.

## Assumptions

- Floors are 1 to n; floor 1 is the lobby. Cars start at floor 1.
- One tick is one floor. Stops are free by default (the brief doesn't say otherwise); `--dwell` adds time per stop, and every experiment is also run at dwell 1.
- In a tick a car drops off, picks a direction, boards, then moves. The log records the floor before the move.
- Passengers board only their assigned car, only when it's going their way, first come first served.
- Express cars only get trips where they serve both floors.
- Bad input (floor out of range, source = dest, duplicate id, negative time) is rejected up front.
- Synthetic traffic uses Poisson arrivals and fixed trip mixes per pattern.

## Trade-offs

- **ETD** optimises the brief's objective directly, but it is greedy: it can't see future arrivals, which costs capacity near saturation.
- **LOOK** leaves little to choose once riders are aboard. A look-ahead router I tried gained 1-4% and nothing on top of ETD, so I removed it.
- **Forecasts reuse the engine's code**, so they can't drift from the real rules, at the cost of speed.
- **The reserved seat** costs one seat, only while someone is overdue. My first version, which let only the overdue passenger board, wrecked throughput.

## Limitations

- ETD slows down when one car has a long queue (each forecast replays it tick by tick).
- Idle cars stay where they stop; there is no parking.
- Constant speed, fixed door time, synthetic traffic: good for comparing dispatchers, not for absolute predictions.

## With more time

- Make ETD account for future arrivals, or switch to grouping by destination when the morning rush is detected.
- Park idle cars where requests have been coming from.
- Solve small cases exactly to measure how far ETD is from optimal.
- Cache forecasts within a tick and cap their length.
- Run real building logs through it.

## Time spent

About 8 hours.
