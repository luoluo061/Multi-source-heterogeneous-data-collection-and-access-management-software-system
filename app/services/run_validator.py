from app.services.run_state import RunStatus
from app.services.state_machine import RunStateMachine


class RunValidator:
    """Validates run transitions."""

    @staticmethod
    def ensure_transition(current: RunStatus, target: RunStatus) -> None:
        if not RunStateMachine.can_transition(current, target):
            raise ValueError(f"Invalid transition from {current} to {target}")
