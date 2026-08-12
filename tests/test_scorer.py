from towerctl_core.events import RUN_COMPLETED, Event
from towerctl_core.models import AgentSpec, Run

from evals.main import SCORES, handle_completed, score_run


def test_score_run():
    assert score_run("hello", "succeeded") == 1.0
    assert score_run("", "succeeded") == 0.5
    assert score_run("hello", "failed") == 0.0


class FakeClient:
    def __init__(self):
        self.agent = AgentSpec(name="e", kind="echo")
        self.run = Run(agent_id=self.agent.id, input="x", output="x")

    def get_run(self, run_id):
        return self.run


def test_handle_completed():
    SCORES.clear()
    client = FakeClient()
    ev = Event(
        topic=RUN_COMPLETED,
        payload={
            "run_id": client.run.id,
            "agent_id": client.agent.id,
            "status": "succeeded",
            "duration_s": 0.01,
        },
    )
    s = handle_completed(ev, client=client)
    assert s.score == 1.0
    assert len(SCORES) == 1
