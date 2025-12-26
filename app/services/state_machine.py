from app.services.run_state import RunStatus


class RunStateMachine:
    """Validates and transitions run states."""

    allowed_transitions = {
        RunStatus.PENDING: {RunStatus.RUNNING, RunStatus.CANCELED},
        RunStatus.RUNNING: {RunStatus.SUCCESS, RunStatus.FAILED, RunStatus.CANCELED},
        RunStatus.SUCCESS: set(),
        RunStatus.FAILED: set(),
        RunStatus.CANCELED: set(),
    }

    @classmethod
    def can_transition(cls, current: RunStatus, target: RunStatus) -> bool:
        return target in cls.allowed_transitions.get(current, set())
