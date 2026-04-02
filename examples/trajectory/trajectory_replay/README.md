# Trajectory Replay Example Library

Reusable library for replaying Nova Act trajectories with browser state validation and HTML report generation.

## Structure

```
trajectory_replay/
├── types.py               # Trajectory data models and replay result types
├── validators.py          # URL, screenshot, and DOM validators
├── runner.py              # TrajectoryRunner, loaders, and replay helper
└── report_compiler.py     # HTML report generation from replay results
```

## runner.py

### `TrajectoryRunner`

Replays a serialized `Trajectory` in a browser session. At each step, validates the current browser state against the original recording before executing the step's program. Produces a `TrajectoryReplayResult` with per-step validation outcomes. Key configuration options include `strict_validators` (raise vs warn on validation failures), custom validator overrides for URL/screenshot/DOM, and `wait_before_replay_ms` for pages with slow client-side rendering.

See [`replay.py`](../replay.py) and [`auto_replay.py`](../auto_replay.py) for usage.

### Helper functions

- `load_trajectory(path)` loads a single `Trajectory` from a JSON file path
- `load_trajectories(directory)` loads all trajectory files from a directory, sorted by start time
- `replay_trajectory(nova, trajectory, ...)` replays a trajectory in an active `NovaAct` session with validation and report generation

## validators.py

All validators extend `ValidatorBase` and implement `validate()` and `handle_result()`. Each has a configurable `tolerance` threshold and supports strict (raise) or lenient (warn) mode.

- `DefaultUrlValidator` compares URL components (scheme, netloc, path by default, configurable). Defaults to exact match.
- `DefaultImageValidator` compares screenshots via pixel diff. Defaults to 10% tolerance. Supports optional `target_boundary` for cropped comparisons.
- `DefaultDOMValidator` compares simplified DOM via string diff. Defaults to 10% tolerance.

## report_compiler.py

### `TrajectoryReportCompiler`

Generates an HTML report from a `TrajectoryReplayResult` with side-by-side expected/observed screenshots, per-step validation results, and expandable diffs for failed validations.
