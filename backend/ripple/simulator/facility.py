"""Tick loop advancing hidden state: temperatures, flow, valve states, faults. No hydraulic physics."""

from ripple.simulator.ground_truth import GroundTruth


class Facility:
    def __init__(self, truth: GroundTruth) -> None:
        self.truth = truth

    def tick(self, dt: float) -> None:
        """Advance simulated state by dt seconds."""
        raise NotImplementedError("TODO(siddharth): facility dynamics")
