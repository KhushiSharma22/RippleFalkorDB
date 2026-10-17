"""The core loop: observe -> update evidence -> query dependencies -> identify uncertainty ->
inspect -> evaluate plans -> validate -> execute -> verify (-> replan on failure)."""

class Orchestrator:
    def run_incident(self, incident_id: str) -> str:
        """Run the loop for an incident until verified recovery or give-up; return Decision id."""
        raise NotImplementedError("TODO(siddharth): core loop")
