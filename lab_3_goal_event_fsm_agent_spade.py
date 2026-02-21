"""
LAB 3: Goal-Event FSM Agent (SPADE Version)

This module implements agoal-event finite state machine (FSM) agent using SPADE 
for disaster response scenarios.
"""

import asyncio
import random
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State
from environment import DisasterEnvironment, DisasterEvent, EnvironmentPercept, Severity


# XMPP Configuration
XMPP_SERVER = "localhost"
RESPONSE_JID = f"response_agent@{XMPP_SERVER}"
RESPONSE_PASSWORD = "response123"


class ResponseState(Enum):
    """Finite states for the disaster response agent"""
    MONITORING = "MONITORING"
    ASSESSING = "ASSESSING"
    DISPATCHING = "DISPATCHING"
    RECOVERY = "RECOVERY"


@dataclass
class AgentGoals:
    """Data class to represent the goals of the agent"""
    rescue_people: str = "Minimize casualties through rapid rescue operations"
    stabilize_infrastructure: str = "Stabilize critical infrastructure to prevent further damage"
    optimize_resources: str = "Optimize resource allocation for maximum efficiency"


class MonitoringState(State):
    """MONITORING state - continuous surveillance of all zones"""
    
    async def run(self):
        agent_data = self.agent.agent_data
        agent_data["_log_trace"]("Action: Continue periodic monitoring")
        
        # Check for events
        events = agent_data["events"]
        
        if events:
            # Transition to ASSESSING
            agent_data["_switch_state"](ResponseState.MONITORING, ResponseState.ASSESSING,
                                      "Disaster-related event detected")
            self.set_next_state(ResponseState.ASSESSING.value)
        else:
            # Stay in MONITORING
            self.set_next_state(ResponseState.MONITORING.value)
        
        await asyncio.sleep(1)


class AssessingState(State):
    """ASSESSING state - evaluating disaster severity and impact"""
    
    async def run(self):
        agent_data = self.agent.agent_data
        events = agent_data["events"]
        
        # Prioritize disaster
        priority_disaster = agent_data["_prioritize_disaster"](events)
        
        if priority_disaster:
            agent_data["_log_trace"](
                f"Assessment: Prioritize {priority_disaster.disaster_type.value} at "
                f"{priority_disaster.location.name} (Severity {priority_disaster.severity.name})"
            )
            agent_data["priority_disaster"] = priority_disaster
        
        # Transition to DISPATCHING
        agent_data["_switch_state"](ResponseState.ASSESSING, ResponseState.DISPATCHING,
                                  "Assessment complete")
        self.set_next_state(ResponseState.DISPATCHING.value)
        await asyncio.sleep(0.5)


class DispatchingState(State):
    """DISPATCHING state - allocating resources and coordinating response"""
    
    async def run(self):
        agent_data = self.agent.agent_data
        priority_disaster = agent_data.get("priority_disaster")
        goals = agent_data["goals"]
        
        if priority_disaster:
            teams = priority_disaster.resources_needed.get("rescue_teams", 0)
            medical = priority_disaster.resources_needed.get("medical_kits", 0)
            agent_data["_log_trace"](
                f"Dispatch: Send {teams} rescue teams and {medical} medical kits "
                f"to {priority_disaster.location.name}"
            )
            agent_data["_log_trace"](f"Goal Alignment: {goals.rescue_people}")
            agent_data["_log_trace"](f"Goal Alignment: {goals.optimize_resources}")
        
        # Transition to RECOVERY
        agent_data["_switch_state"](ResponseState.DISPATCHING, ResponseState.RECOVERY,
                                  "Initial dispatch actions completed")
        self.set_next_state(ResponseState.RECOVERY.value)
        await asyncio.sleep(0.5)


class RecoveryState(State):
    """RECOVERY state - stabilization and infrastructure restoration"""
    
    async def run(self):
        agent_data = self.agent.agent_data
        priority_disaster = agent_data.get("priority_disaster")
        goals = agent_data["goals"]
        
        if priority_disaster:
            if priority_disaster.severity.value <= Severity.MODERATE.value:
                agent_data["_log_trace"]("Recovery: Situation is stabilizing; downgrade response level")
                agent_data["_switch_state"](ResponseState.RECOVERY, ResponseState.MONITORING,
                                          "Disaster impact under control")
                self.set_next_state(ResponseState.MONITORING.value)
            else:
                agent_data["_log_trace"]("Recovery: Continue containment and infrastructure stabilization")
                agent_data["_log_trace"](f"Goal Alignment: {goals.stabilize_infrastructure}")
                agent_data["_switch_state"](ResponseState.RECOVERY, ResponseState.MONITORING,
                                          "Return to monitor after recovery cycle")
                self.set_next_state(ResponseState.MONITORING.value)
        else:
            self.set_next_state(ResponseState.MONITORING.value)
        
        await asyncio.sleep(0.5)


class GoalReactiveResponseAgent(Agent):
    """
    SPADE-based goal-reactive finite state machine (FSM) agent for disaster response
    """
    
    def __init__(self, jid, password, environment: DisasterEnvironment, cycles: int = 8):
        super().__init__(jid, password)
        self.environment = environment
        self.cycles = cycles
        self.current_cycle = 0
        
        # Agent data accessible to all states
        self.agent_data = {
            "goals": AgentGoals(),
            "trace": [],
            "transition_history": [],
            "last_handled_event_ids": set(),
            "events": [],
            "priority_disaster": None,
            "_log_trace": self._log_trace,
            "_switch_state": self._switch_state,
            "_prioritize_disaster": self._prioritize_disaster
        }
        
        self.trace_file = Path("logs/LAB3_execution_logs_spade.txt")
        self.trace_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _timestamp(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _log_trace(self, message: str):
        entry = f"[{self._timestamp()}] {self.jid.localpart} | {message}"
        self.agent_data["trace"].append(entry)
        print(entry)
    
    def _switch_state(self, old_state: ResponseState, new_state: ResponseState, reason: str):
        """Log state transitions"""
        self.agent_data["transition_history"].append({
            "from": old_state.name,
            "to": new_state.name,
            "reason": reason,
            "timestamp": self._timestamp()
        })
        self._log_trace(f"STATE {old_state.name} -> {new_state.name} | Reason: {reason}")
    
    def _derive_events(self, percepts: List[EnvironmentPercept]) -> List[Dict]:
        """Convert sensor percepts into internal/external event triggers"""
        derived_events = []
        
        for percept in percepts:
            if percept.temperature >= 42:
                derived_events.append({
                    "type": "TEMP_SPIKE",
                    "location": percept.location.name,
                    "details": f"Temperature at {percept.temperature:.1f}°C"
                })
            
            if percept.water_level >= 1.5:
                derived_events.append({
                    "type": "WATER_RISE",
                    "location": percept.location.name,
                    "details": f"Water level at {percept.water_level:.2f}m"
                })
            
            for disaster in percept.active_disasters:
                if disaster.event_id not in self.agent_data["last_handled_event_ids"]:
                    derived_events.append({
                        "type": "DISASTER_DETECTED",
                        "location": percept.location.name,
                        "disaster": disaster,
                        "details": f"{disaster.disaster_type.value} ({disaster.severity.name})"
                    })
                    self.agent_data["last_handled_event_ids"].add(disaster.event_id)
                
                if disaster.severity.value >= Severity.CRITICAL.value:
                    derived_events.append({
                        "type": "SEVERITY_ESCALATION",
                        "location": percept.location.name,
                        "disaster": disaster,
                        "details": f"Severity is {disaster.severity.name}"
                    })
                
                if disaster.resources_needed.get("rescue_teams", 0) >= 12:
                    derived_events.append({
                        "type": "RESOURCE_SHORTAGE",
                        "location": percept.location.name,
                        "disaster": disaster,
                        "details": "High rescue-team requirement"
                    })
        
        return derived_events
    
    def _prioritize_disaster(self, events: List[Dict]) -> Optional[DisasterEvent]:
        """Determine which disaster event to prioritize"""
        disasters = [event["disaster"] for event in events if "disaster" in event]
        
        if not disasters:
            return None
        
        return max(disasters, key=lambda disaster: (
            disaster.severity.value,
            disaster.casualties,
            disaster.infrastructure_damage
        ))
    
    def _save_trace(self):
        """Save execution trace to file"""
        with open(self.trace_file, "w", encoding="utf-8") as f:
            f.write("LAB 3 EXECUTION TRACE (SPADE VERSION)\n")
            f.write("=" * 90 + "\n")
            f.write(f"Agent: {self.jid}\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")
            
            f.write("GOALS\n")
            goals = self.agent_data["goals"]
            f.write("- " + goals.rescue_people + "\n")
            f.write("- " + goals.stabilize_infrastructure + "\n")
            f.write("- " + goals.optimize_resources + "\n\n")
            
            f.write("TRANSITIONS\n")
            if self.agent_data["transition_history"]:
                for transition in self.agent_data["transition_history"]:
                    f.write(
                        f"[{transition['timestamp']}] {transition['from']} -> {transition['to']} | "
                        f"{transition['reason']}\n"
                    )
            else:
                f.write("No state transitions recorded.\n")
            
            f.write("\nTRACE LOG\n")
            f.write("-" * 90 + "\n")
            for entry in self.agent_data["trace"]:
                f.write(entry + "\n")
    
    class ResponseFSM(FSMBehaviour):
        """FSM Behaviour managing state transitions"""
        
        async def on_start(self):
            agent_data = self.agent.agent_data
            agent_data["_log_trace"]("Starting goal-driven reactive response agent")
            agent_data["_log_trace"](f"Initial state: {ResponseState.MONITORING.name}")
        
        async def on_end(self):
            self.agent._log_trace("FSM Behaviour ended")
            self.agent._save_trace()
            self.agent._log_trace(f"Execution trace saved to {self.agent.trace_file}")
    
    class CycleController(State):
        """Controller state that manages simulation cycles"""
        
        async def run(self):
            agent = self.agent
            agent.current_cycle += 1
            
            agent._log_trace(f"--- CYCLE {agent.current_cycle}/{agent.cycles} ---")
            
            # Update environment
            agent.environment.update_environment()
            percepts = agent.environment.get_all_percepts()
            
            # Derive events
            events = agent._derive_events(percepts)
            agent.agent_data["events"] = events
            
            # Log events
            for event in events:
                agent._log_trace(
                    f"EVENT {event['type']} @ {event['location']} | {event['details']}"
                )
            
            # Check if simulation should continue
            if agent.current_cycle >= agent.cycles:
                agent._log_trace("Simulation completed")
                self.kill()  # End FSM
            else:
                # Continue to MONITORING state
                self.set_next_state(ResponseState.MONITORING.value)
            
            await asyncio.sleep(1)
    
    async def setup(self):
        """Agent setup - called when agent starts"""
        print("\n" + "=" * 90)
        print("LAB 3: Goals, Events, and Reactive Behavior (SPADE Version)")
        print("Disaster Response & Relief Coordination System")
        print("=" * 90)
        print(f"Agent JID: {self.jid}")
        print(f"Cycles: {self.cycles}")
        print("=" * 90 + "\n")
        
        # Create FSM behaviour
        fsm = self.ResponseFSM()
        
        # Add controller state
        fsm.add_state(name="CONTROLLER", state=self.CycleController(), initial=True)
        
        # Add FSM states
        fsm.add_state(name=ResponseState.MONITORING.value, state=MonitoringState())
        fsm.add_state(name=ResponseState.ASSESSING.value, state=AssessingState())
        fsm.add_state(name=ResponseState.DISPATCHING.value, state=DispatchingState())
        fsm.add_state(name=ResponseState.RECOVERY.value, state=RecoveryState())
        
        # Add transitions
        fsm.add_transition(source="CONTROLLER", dest=ResponseState.MONITORING.value)
        fsm.add_transition(source=ResponseState.MONITORING.value, dest=ResponseState.MONITORING.value)
        fsm.add_transition(source=ResponseState.MONITORING.value, dest=ResponseState.ASSESSING.value)
        fsm.add_transition(source=ResponseState.ASSESSING.value, dest=ResponseState.DISPATCHING.value)
        fsm.add_transition(source=ResponseState.DISPATCHING.value, dest=ResponseState.RECOVERY.value)
        fsm.add_transition(source=ResponseState.RECOVERY.value, dest=ResponseState.MONITORING.value)
        fsm.add_transition(source=ResponseState.MONITORING.value, dest="CONTROLLER")
        fsm.add_transition(source=ResponseState.ASSESSING.value, dest="CONTROLLER")
        fsm.add_transition(source=ResponseState.DISPATCHING.value, dest="CONTROLLER")
        fsm.add_transition(source=ResponseState.RECOVERY.value, dest="CONTROLLER")
        
        self.add_behaviour(fsm)


async def main():
    """Main entry point for Lab 3"""
    random.seed(419)
    
    print("\nLAB 3: Goals, Events, and Reactive Behavior (SPADE Version)")
    print("Disaster Response & Relief Coordination System\n")
    
    print(f"XMPP Configuration:")
    print(f"  Server: {XMPP_SERVER}")
    print(f"  Agent JID: {RESPONSE_JID}")
    print(f"  Note: Update XMPP_SERVER variable for remote servers\n")
    
    environment = DisasterEnvironment()
    agent = GoalReactiveResponseAgent(RESPONSE_JID, RESPONSE_PASSWORD, environment, cycles=8)
    
    await agent.start()
    
    print("✓ Response agent is running")
    print("Agent will stop automatically after 8 cycles\n")
    
    # Wait for agent to complete
    while agent.is_alive():
        await asyncio.sleep(1)
    
    print("\n✓ Agent stopped successfully\n")


if __name__ == "__main__":
    asyncio.run(main())
