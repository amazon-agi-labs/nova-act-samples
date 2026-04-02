# Amazon Nova Act Trajectory Examples

Examples demonstrating how to save, replay, and validate trajectory data from Nova Act workflow executions. When `replayable=True` is set on the `NovaAct` constructor, the SDK records a trajectory for each `act()` call, capturing the URL, screenshot, simplified DOM, and actions at every step, and serializes it to a JSON file accessible via `ActResult.trajectory_file_path` and reusable for replay.

## Repository structure

```
├── save.py                    # Save a trajectory from a single act
├── replay.py                  # Replay a saved trajectory with validation
├── auto_replay.py             # ReplayableNovaAct - automatic save/replay per act
└── trajectory_replay/         # Trajectory replay library
```

## Prerequisites

Complete the [Getting Started](../README.md#getting-started) section in the main examples directory before running these examples.

## Usage

### Save a trajectory

#### save.py

Runs a workflow with `replayable=True` and prints the trajectory file path.

```bash
python -m examples.trajectory.save
```

| Parameter | Required | Default | Description |
|---|---|---|---|
| `logs_directory` | No | `logs/` | Directory to write session logs and trajectory files to |

**Implementation details:**
- Sets `replayable=True` on the `NovaAct` constructor
- Uses `ActResult.trajectory_file_path` to get the path to the saved trajectory JSON
- Prints the trajectory file path on completion — pass this to `replay.py` as `--trajectory_file`

### Replay trajectories

The replay examples use the [trajectory replay example library](trajectory_replay/README.md). The `TrajectoryRunner` replays each step from the saved trajectory, validating the browser state against the original recording using configurable [validators](trajectory_replay/README.md#validators) for URL, screenshot, and DOM comparison. By default, validation failures raise errors; set `strict_validators=False` on `TrajectoryRunner` to log warnings instead. After replay, the `TrajectoryReportCompiler` generates an HTML report with side-by-side screenshot comparisons and per-step validation results. Helper functions like `load_trajectory` and `replay_trajectory` are also provided. See the [trajectory replay example library](trajectory_replay/README.md) for full implementation reference and configuration options.

#### replay.py

Loads a trajectory JSON file and replays it in a new browser session with validation. Pass the trajectory file path printed by `save.py` as the `--trajectory_file` argument.

```bash
python -m examples.trajectory.replay --trajectory_file=<path_to_trajectory.json>
```

| Parameter | Required | Default | Description |
|---|---|---|---|
| `trajectory_file` | Yes | - | Path to trajectory JSON file |
| `starting_page` | No | First step's URL | Browser starting page for the replay session |
| `strict` | No | `True` | If `True`, validation failures raise errors. If `False`, they log warnings |

**Implementation details:**
- `load_trajectory` deserializes the trajectory JSON into the `Trajectory` type
- `replay_trajectory` constructs a `TrajectoryRunner` and executes the trajectory with validation

#### auto_replay.py

Uses `ReplayableNovaAct`, a subclass of `NovaAct` that overrides `act()` to automatically save each trajectory on first run and replay from the saved file on subsequent runs. Write your workflows normally and the save/replay logic is handled transparently.

```bash
python -m examples.trajectory.auto_replay
```

| Parameter | Required | Default | Description |
|---|---|---|---|
| `strict` | No | `True` | If `True`, validation failures raise errors. If `False`, they log warnings |

**Implementation details:**
- `ReplayableNovaAct` forces `replayable=True` and overrides `act()`
- On first run, saves the trajectory using `ActResult.trajectory_file_path` to a `trajectories/` directory with an index prefix for ordering
- On subsequent runs, detects saved trajectories by index and replays them
- Returns `ActResult` on first run, `None` during replay (the saved trajectory JSON contains the original `ActMetadata` fields if you need to reconstruct one)

## Next steps

- For library internals, see [trajectory_replay/](trajectory_replay/README.md)
- For production deployments, see [CDK](../../cdk/README.md)
- For complete applications, see [Solutions](../../solutions/README.md)
- Visit the [Nova Act documentation](https://docs.aws.amazon.com/nova-act)
