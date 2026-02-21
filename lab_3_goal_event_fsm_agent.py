"""
LAB 3: Goal-Event FSM Agent

This module implements a goal-event finite state machine (FSM) agent for disaster response scenarios.
"""

import asyncio
import random
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

from environment import DisasterEnvironment, DisasterEvent, EnvironmentPercept, Severity


class ResponseState(Enum):
    """
    Finite states for the disaster response agent
    """
    MONITORING = "monitoring"
    ASSESSING = "assessing"
    DISPATCHING = "dispatching"
    RECOVERY = "recovering"

@dataclass
class AgentGoals:
    """
    Data class to represent the goals of the agent
    """
    rescue_people: str = "Minimize casualties through rapid rescue operations"
    stabilize_infrastructure: str = "Stabilize critical infrastructure to prevent further damage"
    optimize_resources: str = "Optimize resource allocation for maximum efficiency"


class GoalReactiveResponseAgent:
    """
    A goal-reactive finite state machine (FSM) agent for disaster response scenarios.
    """

    def __init__(self, agent_id: str, environment: DisasterEnvironment):
        self.agent_id = agent_id
        self.environment = environment
        self.state = ResponseState.MONITORING
        self.goals = AgentGoals()
        self.trace: List[str] = []
        self.transition_history: List[Dict[str, str]] = []
        self.last_handled_event_ids: Set[str] = set()

        self.trace_file = Path("logs/LAB3_execution_logs.txt")
        self.trace_file.parent.mkdir(parents=True, exist_ok=True)

    
    def _timestamp(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _log_trace(self, message: str):
        entry = f"[{self._timestamp()}] {self.agent_id} | {message}"
        self.trace.append(entry)
        print(entry) 

    def _switch_state(self, new_state: ResponseState, reason: str):
        old_state = self.state

        if old_state == new_state:
            return
        
        self.state = new_state
        self.transition_history.append({
            "from": old_state.name,
            "to": new_state.name,
            "reason": reason,
            "timestamp": self._timestamp()
        })

        self._log_trace(f"STATE {old_state.name} -> {new_state.name} | Reason: {reason}")

    
    def _derive_events(self, percepts: List[EnvironmentPercept]) -> List[Dict[str, object]]:
        """Convert sensor percepts into internal/external event triggers."""
        derived_events: List[Dict[str, object]] = []

        for percept in percepts:
            if percept.temperature >= 42:
                derived_events.append(
                    {
                        "type": "TEMP_SPIKE",
                        "location": percept.location.name,
                        "details": f"Temperature at {percept.temperature:.1f}°C",
                    }
                )

            if percept.water_level >= 1.5:
                derived_events.append(
                    {
                        "type": "WATER_RISE",
                        "location": percept.location.name,
                        "details": f"Water level at {percept.water_level:.2f}m",
                    }
                )

            for disaster in percept.active_disasters:
                if disaster.event_id not in self.last_handled_event_ids:
                    derived_events.append(
                        {
                            "type": "DISASTER_DETECTED",
                            "location": percept.location.name,
                            "disaster": disaster,
                            "details": f"{disaster.disaster_type.value} ({disaster.severity.name})",
                        }
                    )
                    self.last_handled_event_ids.add(disaster.event_id)

                if disaster.severity.value >= Severity.CRITICAL.value:
                    derived_events.append(
                        {
                            "type": "SEVERITY_ESCALATION",
                            "location": percept.location.name,
                            "disaster": disaster,
                            "details": f"Severity is {disaster.severity.name}",
                        }
                    )

                if disaster.resources_needed.get("rescue_teams", 0) >= 12:
                    derived_events.append(
                        {
                            "type": "RESOURCE_SHORTAGE",
                            "location": percept.location.name,
                            "disaster": disaster,
                            "details": "High rescue-team requirement",
                        }
                    )

        return derived_events
    
    def _prioritize_disaster(self, events: List[Dict[str, object]]) -> Optional[DisasterEvent]:
        """Determine which disaster event to prioritize based on severity and resource needs."""
        disasters = [event["disaster"] for event in events if "disaster" in event]

        if not disasters:
            return None
        
        return max(disasters, key=lambda disaster: (
            disaster.severity.value,
            disaster.casualties,
            disaster.infrastructure_damage
        ))
    
    def _react(self, events: List[Dict[str, object]]):
        """Reactive behavior rules implemented as an FSM policy."""
        if not events:
            if self.state != ResponseState.MONITORING:
                self._switch_state(ResponseState.MONITORING, "No active trigger events")
            self._log_trace("Action: Continue periodic monitoring")
            return

        for event in events:
            self._log_trace(
                f"EVENT {event['type']} @ {event['location']} | {event['details']}"
            )

        priority_disaster = self._prioritize_disaster(events)

        if self.state == ResponseState.MONITORING:
            self._switch_state(ResponseState.ASSESSING, "Disaster-related event detected")

        if self.state == ResponseState.ASSESSING:
            if priority_disaster:
                self._log_trace(
                    "Assessment: "
                    f"Prioritize {priority_disaster.disaster_type.value} at "
                    f"{priority_disaster.location.name} (Severity {priority_disaster.severity.name})"
                )
            self._switch_state(ResponseState.DISPATCHING, "Assessment complete")

        if self.state == ResponseState.DISPATCHING:
            if priority_disaster:
                teams = priority_disaster.resources_needed.get("rescue_teams", 0)
                medical = priority_disaster.resources_needed.get("medical_kits", 0)
                self._log_trace(
                    f"Dispatch: Send {teams} rescue teams and {medical} medical kits "
                    f"to {priority_disaster.location.name}"
                )
                self._log_trace(f"Goal Alignment: {self.goals.rescue_people}")
                self._log_trace(f"Goal Alignment: {self.goals.optimize_resources}")

            self._switch_state(ResponseState.RECOVERY, "Initial dispatch actions completed")

        if self.state == ResponseState.RECOVERY:
            if priority_disaster:
                if priority_disaster.severity.value <= Severity.MODERATE.value:
                    self._log_trace("Recovery: Situation is stabilizing; downgrade response level")
                    self._switch_state(ResponseState.MONITORING, "Disaster impact under control")
                else:
                    self._log_trace("Recovery: Continue containment and infrastructure stabilization")
                    self._log_trace(f"Goal Alignment: {self.goals.stabilize_infrastructure}")
                    self._switch_state(ResponseState.MONITORING, "Return to monitor after recovery cycle")

    def _save_trace(self):
        with open(self.trace_file, "w") as trace_handle:
            trace_handle.write("LAB 3 EXECUTION TRACE\n")
            trace_handle.write("=" * 90 + "\n")
            trace_handle.write(f"Agent: {self.agent_id}\n")
            trace_handle.write(f"Generated: {datetime.now().isoformat()}\n\n")

            trace_handle.write("GOALS\n")
            trace_handle.write("- " + self.goals.rescue_people + "\n")
            trace_handle.write("- " + self.goals.stabilize_infrastructure + "\n")
            trace_handle.write("- " + self.goals.optimize_resources + "\n\n")

            trace_handle.write("TRANSITIONS\n")
            if self.transition_history:
                for transition in self.transition_history:
                    trace_handle.write(
                        f"[{transition['timestamp']}] {transition['from']} -> {transition['to']} | "
                        f"{transition['reason']}\n"
                    )
            else:
                trace_handle.write("No state transitions recorded.\n")

            trace_handle.write("\nTRACE LOG\n")
            trace_handle.write("-" * 90 + "\n")
            for entry in self.trace:
                trace_handle.write(entry + "\n")

    async def run(self, cycles: int = 8, interval_seconds: int = 2):
        self._log_trace("Starting goal-driven reactive response agent")
        self._log_trace(f"Initial state: {self.state.name}")

        for cycle in range(1, cycles + 1):
            self._log_trace(f"--- CYCLE {cycle}/{cycles} ---")
            self.environment.update_environment()
            percepts = self.environment.get_all_percepts()
            events = self._derive_events(percepts)
            self._react(events)
            await asyncio.sleep(interval_seconds)

        self._log_trace("Simulation completed")
        self._save_trace()
        self._log_trace(f"Execution trace saved to {self.trace_file}")


async def main():
    print("\nLAB 3: Goals, Events, and Reactive Behavior")
    print("Disaster Response & Relief Coordination System\n")

    random.seed(419)

    environment = DisasterEnvironment()
    agent = GoalReactiveResponseAgent(agent_id="RESPONSE-001", environment=environment)
    await agent.run(cycles=8, interval_seconds=1)


if __name__ == "__main__":
    asyncio.run(main())