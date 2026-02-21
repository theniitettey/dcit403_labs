"""
LAB 4: Agent Communication Using FIPA-ACL (SPADE Version)

This module implements inter-agent communication using SPADE's built-in FIPA-ACL 
messaging capabilities for disaster response coordination.
"""

import asyncio
import json
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template

from environment import DisasterEnvironment, DisasterEvent, Location, Severity


# XMPP Configuration
XMPP_SERVER = "localhost"
SENSOR_JID = f"sensor_comm@{XMPP_SERVER}"
RESPONSE_JID = f"response_comm@{XMPP_SERVER}"
COORDINATOR_JID = f"coordinator_comm@{XMPP_SERVER}"
PASSWORD = "lab4pass"


class SensorCommunicatorAgent(Agent):
    """
    Sensor agent that detects disasters and sends INFORM messages via SPADE
    """
    
    def __init__(self, jid, password, environment: DisasterEnvironment):
        super().__init__(jid, password)
        self.environment = environment
        self.conversation_counter = 0
        self.trace = []
        
    def _generate_conversation_id(self) -> str:
        self.conversation_counter += 1
        return f"CONV-{self.jid.localpart}-{self.conversation_counter}"
    
    def _timestamp(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _log_trace(self, message: str):
        entry = f"[{self._timestamp()}] {self.jid.localpart} | {message}"
        self.trace.append(entry)
        print(entry)
    
    class DetectAndInformBehaviour(CyclicBehaviour):
        """Detect disasters and send INFORM messages"""
        
        async def run(self):
            # Update environment
            self.agent.environment.update_environment()
            percepts = self.agent.environment.get_all_percepts()
            
            # Check each location for disasters
            for percept in percepts:
                if percept.active_disasters:
                    disaster = percept.active_disasters[0]
                    
                    # Create FIPA-ACL INFORM message
                    msg = Message(to=RESPONSE_JID)
                    msg.set_metadata("performative", "inform")
                    msg.set_metadata("ontology", "disaster-response")
                    msg.set_metadata("protocol", "disaster-alert")
                    msg.set_metadata("conversation-id", self.agent._generate_conversation_id())
                    
                    # Set message body with disaster information
                    content = {
                        "message_type": "disaster_detected",
                        "location": percept.location.name,
                        "disaster_type": disaster.disaster_type.value,
                        "severity": disaster.severity.name,
                        "casualties": disaster.casualties,
                        "infrastructure_damage": disaster.infrastructure_damage,
                        "resources_needed": disaster.resources_needed,
                        "event_id": disaster.event_id
                    }
                    msg.body = json.dumps(content)
                    
                    # Send message
                    await self.send(msg)
                    self.agent._log_trace(
                        f"SEND INFORM to {RESPONSE_JID.split('@')[0]} | "
                        f"Conv:{msg.get_metadata('conversation-id')} | "
                        f"{disaster.disaster_type.value} at {percept.location.name}"
                    )
            
            await asyncio.sleep(3)
    
    async def setup(self):
        self._log_trace(f"SensorCommunicatorAgent started")
        b = self.DetectAndInformBehaviour()
        self.add_behaviour(b)


class ResponseAgent(Agent):
    """
    Response agent that receives INFORM messages and sends REQUEST messages
    """
    
    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.active_disasters = {}
        self.trace = []
    
    def _timestamp(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _log_trace(self, message: str):
        entry = f"[{self._timestamp()}] {self.jid.localpart} | {message}"
        self.trace.append(entry)
        print(entry)
    
    class ReceiveInformBehaviour(CyclicBehaviour):
        """Receive INFORM messages and process them"""
        
        async def run(self):
            # Wait for INFORM messages
            msg = await self.receive(timeout=10)
            
            if msg:
                performative = msg.get_metadata("performative")
                
                if performative == "inform":
                    content = json.loads(msg.body)
                    self.agent._log_trace(
                        f"RECV INFORM from {msg.sender.localpart} | "
                        f"Conv:{msg.get_metadata('conversation-id')} | "
                        f"{content.get('disaster_type')} at {content.get('location')}"
                    )
                    
                    # Store disaster information
                    event_id = content.get("event_id")
                    self.agent.active_disasters[event_id] = content
                    
                    # Send REQUEST to coordinator
                    await self._request_resources(msg, content)
                
                elif performative == "agree":
                    content = json.loads(msg.body)
                    self.agent._log_trace(
                        f"RECV AGREE from {msg.sender.localpart} | "
                        f"Conv:{msg.get_metadata('conversation-id')} | "
                        f"Resources allocated"
                    )
                
                elif performative == "refuse":
                    content = json.loads(msg.body)
                    self.agent._log_trace(
                        f"RECV REFUSE from {msg.sender.localpart} | "
                        f"Conv:{msg.get_metadata('conversation-id')} | "
                        f"Reason: {content.get('reason')}"
                    )
                
                elif performative == "confirm":
                    content = json.loads(msg.body)
                    self.agent._log_trace(
                        f"RECV CONFIRM from {msg.sender.localpart} | "
                        f"Conv:{msg.get_metadata('conversation-id')} | "
                        f"{content.get('message')}"
                    )
            
            await asyncio.sleep(0.1)
        
        async def _request_resources(self, inform_msg: Message, content: Dict):
            """Send REQUEST message to coordinator"""
            request_msg = Message(to=COORDINATOR_JID)
            request_msg.set_metadata("performative", "request")
            request_msg.set_metadata("ontology", "disaster-response")
            request_msg.set_metadata("protocol", "resource-allocation")
            request_msg.set_metadata("conversation-id", inform_msg.get_metadata("conversation-id"))
            request_msg.set_metadata("in-reply-to", inform_msg.get_metadata("conversation-id"))
            
            request_content = {
                "action": "allocate_resources",
                "disaster_location": content["location"],
                "disaster_type": content["disaster_type"],
                "severity": content["severity"],
                "resources_needed": content["resources_needed"],
                "event_id": content["event_id"]
            }
            request_msg.body = json.dumps(request_content)
            
            await self.send(request_msg)
            self.agent._log_trace(
                f"SEND REQUEST to {COORDINATOR_JID.split('@')[0]} | "
                f"Conv:{request_msg.get_metadata('conversation-id')} | "
                f"Request resources for {content['location']}"
            )
    
    async def setup(self):
        self._log_trace(f"ResponseAgent started")
        b = self.ReceiveInformBehaviour()
        template = Template()
        template.set_metadata("performative", "inform")
        self.add_behaviour(b, template)
        
        # Also listen for agree, refuse, confirm
        b2 = self.ReceiveInformBehaviour()
        template2 = Template()
        template2.set_metadata("performative", "agree", "refuse", "confirm")
        self.add_behaviour(b2, template2)


class CoordinatorAgent(Agent):
    """
    Coordinator agent that handles resource allocation requests
    """
    
    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.available_resources = {
            "rescue_teams": 20,
            "medical_kits": 100,
            "fire_trucks": 10,
            "ambulances": 15
        }
        self.allocated_resources = {}
        self.trace = []
    
    def _timestamp(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _log_trace(self, message: str):
        entry = f"[{self._timestamp()}] {self.jid.localpart} | {message}"
        self.trace.append(entry)
        print(entry)
    
    class HandleRequestBehaviour(CyclicBehaviour):
        """Handle REQUEST messages for resource allocation"""
        
        async def run(self):
            msg = await self.receive(timeout=10)
            
            if msg:
                performative = msg.get_metadata("performative")
                
                if performative == "request":
                    content = json.loads(msg.body)
                    self.agent._log_trace(
                        f"RECV REQUEST from {msg.sender.localpart} | "
                        f"Conv:{msg.get_metadata('conversation-id')} | "
                        f"Action: {content.get('action')}"
                    )
                    
                    if content.get("action") == "allocate_resources":
                        await self._allocate_resources(msg, content)
            
            await asyncio.sleep(0.1)
        
        async def _allocate_resources(self, request_msg: Message, content: Dict):
            """Allocate resources and send AGREE/REFUSE + CONFIRM"""
            resources_needed = content.get("resources_needed", {})
            event_id = content.get("event_id")
            
            # Filter managed resources
            managed_resources = {}
            for resource, amount in resources_needed.items():
                if resource in self.agent.available_resources:
                    managed_resources[resource] = amount
            
            # Check availability
            can_allocate = True
            if managed_resources:
                for resource, amount in managed_resources.items():
                    if self.agent.available_resources.get(resource, 0) < amount:
                        can_allocate = False
                        break
            else:
                can_allocate = False
            
            conversation_id = request_msg.get_metadata("conversation-id")
            
            if can_allocate:
                # Send AGREE
                agree_msg = Message(to=str(request_msg.sender))
                agree_msg.set_metadata("performative", "agree")
                agree_msg.set_metadata("ontology", "disaster-response")
                agree_msg.set_metadata("protocol", "resource-allocation")
                agree_msg.set_metadata("conversation-id", conversation_id)
                agree_msg.set_metadata("in-reply-to", conversation_id)
                
                agree_content = {
                    "action": "allocate_resources",
                    "resources_allocated": managed_resources,
                    "location": content["disaster_location"],
                    "event_id": event_id
                }
                agree_msg.body = json.dumps(agree_content)
                
                # Deduct resources
                for resource, amount in managed_resources.items():
                    self.agent.available_resources[resource] -= amount
                
                self.agent.allocated_resources[event_id] = managed_resources
                
                await self.send(agree_msg)
                self.agent._log_trace(
                    f"SEND AGREE to {request_msg.sender.localpart} | "
                    f"Conv:{conversation_id} | "
                    f"Resources: {managed_resources}"
                )
                
                # Send CONFIRM
                confirm_msg = Message(to=str(request_msg.sender))
                confirm_msg.set_metadata("performative", "confirm")
                confirm_msg.set_metadata("ontology", "disaster-response")
                confirm_msg.set_metadata("protocol", "resource-allocation")
                confirm_msg.set_metadata("conversation-id", conversation_id)
                
                confirm_content = {
                    "message": f"Resources allocated to {content['disaster_location']}",
                    "allocation": managed_resources,
                    "remaining_resources": self.agent.available_resources.copy()
                }
                confirm_msg.body = json.dumps(confirm_content)
                
                await self.send(confirm_msg)
                self.agent._log_trace(
                    f"SEND CONFIRM to {request_msg.sender.localpart} | "
                    f"Conv:{conversation_id} | "
                    f"Allocation complete"
                )
            
            else:
                # Send REFUSE
                refuse_msg = Message(to=str(request_msg.sender))
                refuse_msg.set_metadata("performative", "refuse")
                refuse_msg.set_metadata("ontology", "disaster-response")
                refuse_msg.set_metadata("protocol", "resource-allocation")
                refuse_msg.set_metadata("conversation-id", conversation_id)
                refuse_msg.set_metadata("in-reply-to", conversation_id)
                
                refuse_reason = "Insufficient resources" if managed_resources else "No managed resources"
                refuse_content = {
                    "action": "allocate_resources",
                    "reason": refuse_reason,
                    "available_resources": self.agent.available_resources.copy(),
                    "requested_resources": managed_resources
                }
                refuse_msg.body = json.dumps(refuse_content)
                
                await self.send(refuse_msg)
                self.agent._log_trace(
                    f"SEND REFUSE to {request_msg.sender.localpart} | "
                    f"Conv:{conversation_id} | "
                    f"Reason: {refuse_reason}"
                )
    
    async def setup(self):
        self._log_trace(f"CoordinatorAgent started")
        self._log_trace(f"Initial resources: {self.available_resources}")
        b = self.HandleRequestBehaviour()
        template = Template()
        template.set_metadata("performative", "request")
        self.add_behaviour(b, template)


async def main():
    """Main entry point for Lab 4"""
    random.seed(404)
    
    print("\n" + "=" * 90)
    print("LAB 4: Agent Communication Using FIPA-ACL (SPADE Version)")
    print("Disaster Response & Relief Coordination System")
    print("=" * 90 + "\n")
    
    print(f"XMPP Configuration:")
    print(f"  Server: {XMPP_SERVER}")
    print(f"  Sensor Agent: {SENSOR_JID}")
    print(f"  Response Agent: {RESPONSE_JID}")
    print(f"  Coordinator Agent: {COORDINATOR_JID}")
    print(f"  Note: Update XMPP_SERVER variable for remote servers\n")
    
    # Create environment
    environment = DisasterEnvironment()
    
    # Create and start agents
    sensor = SensorCommunicatorAgent(SENSOR_JID, PASSWORD, environment)
    response = ResponseAgent(RESPONSE_JID, PASSWORD)
    coordinator = CoordinatorAgent(COORDINATOR_JID, PASSWORD)
    
    await sensor.start()
    await response.start()
    await coordinator.start()
    
    print("✓ All agents started successfully\n")
    print("=" * 90)
    print("Agents are communicating via FIPA-ACL messages over XMPP")
    print("Press Ctrl+C to stop")
    print("=" * 90 + "\n")
    
    try:
        # Run for a specified duration
        await asyncio.sleep(30)  # Run for 30 seconds
    except KeyboardInterrupt:
        print("\n\nStopping agents...")
    
    # Stop all agents
    await sensor.stop()
    await response.stop()
    await coordinator.stop()
    
    print("\n✓ All agents stopped successfully\n")
    
    # Save trace logs
    trace_file = Path("logs/LAB4_communication_logs_spade.txt")
    trace_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(trace_file, "w", encoding="utf-8") as f:
        f.write("LAB 4 EXECUTION TRACE - FIPA-ACL COMMUNICATION (SPADE VERSION)\n")
        f.write("=" * 90 + "\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n\n")
        
        f.write("COMBINED AGENT TRACES\n")
        f.write("=" * 90 + "\n\n")
        
        all_traces = sensor.trace + response.trace + coordinator.trace
        for entry in sorted(all_traces):
            f.write(entry + "\n")
        
        f.write("\n\nRESOURCE ALLOCATION SUMMARY\n")
        f.write("=" * 90 + "\n")
        f.write("Remaining Resources:\n")
        for resource, amount in coordinator.available_resources.items():
            f.write(f"  {resource}: {amount}\n")
        
        f.write("\nAllocated to Disasters:\n")
        for event_id, resources in coordinator.allocated_resources.items():
            f.write(f"  Event {event_id}: {resources}\n")
    
    print(f"Execution trace saved to: {trace_file}\n")


if __name__ == "__main__":
    asyncio.run(main())
