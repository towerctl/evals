"""towerctl evals: scores completed runs.

Consumes: run.completed. Emits: eval.recorded. Serves: GET /v1/scores.

M0 scorer: non-empty-output heuristic (echo agents). M1: assertion-based
scorers per agent + baseline comparison + regression flags.
"""

from __future__ import annotations

import os
import threading

from fastapi import FastAPI
from towerctl_core.bus import bus_from_env
from towerctl_core.client import GatewayClient
from towerctl_core.events import EVAL_RECORDED, RUN_COMPLETED, Event
from towerctl_core.models import EvalScore

app = FastAPI(title="towerctl evals", version="0.1.0")
bus = bus_from_env(group="evals")
SCORES: list[EvalScore] = []


def score_run(run_output: str | None, status: str) -> float:
    """M0 heuristic: succeeded + non-empty output = 1.0."""
    if status != "succeeded":
        return 0.0
    return 1.0 if run_output and run_output.strip() else 0.5


def make_client() -> GatewayClient:
    return GatewayClient(
        base_url=os.environ.get("GATEWAY_URL", "http://localhost:8080"),
        api_key=os.environ.get("TOWERCTL_API_KEY", "dev-key"),
    )


def handle_completed(ev: Event, client: GatewayClient | None = None) -> EvalScore:
    client = client or make_client()
    run = client.get_run(ev.payload["run_id"])
    s = EvalScore(
        run_id=run.id,
        agent_id=run.agent_id,
        score=score_run(run.output, ev.payload["status"]),
        scorer="m0-nonempty",
        detail={"status": ev.payload["status"], "duration_s": ev.payload.get("duration_s")},
    )
    SCORES.append(s)
    bus.publish(
        Event(
            topic=EVAL_RECORDED,
            payload={"run_id": s.run_id, "agent_id": s.agent_id, "score": s.score, "scorer": s.scorer},
        )
    )
    return s


bus.subscribe(RUN_COMPLETED, handle_completed)


@app.get("/healthz")
def healthz() -> dict:
    return {"ok": True, "scores": len(SCORES)}


@app.get("/v1/scores", response_model=list[EvalScore])
def list_scores() -> list[EvalScore]:
    return SCORES


@app.on_event("startup")
def start_consumer() -> None:
    def loop() -> None:
        while True:
            bus.poll(block_ms=2000)

    threading.Thread(target=loop, daemon=True).start()
