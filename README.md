# towerctl/evals

Scores completed runs. Consumes `run.completed`, fetches the run via the
SDK, scores it, stores the verdict, emits `eval.recorded`, and serves
`GET /v1/scores`.

M0 scorer is a non-empty-output heuristic. M1 adds per-agent assertion
scorers, baselines, and regression flags (score drop vs trailing mean).

```bash
pip install -e .[dev]
uvicorn evals.main:app --port 8082
```
