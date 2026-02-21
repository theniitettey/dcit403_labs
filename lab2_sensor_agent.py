"""
LAB 2: Perception and Environment Modeling

This module implements a sensor agent using SPADE that perceives environmental 
conditions and detects disaster events in a simulated environment.
"""

from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour
from datetime import datetime
import asyncio
import random
from environment import DisasterEnvironment, Location


# XMPP Configuration - Update these for your server
XMPP_SERVER = "localhost"  # Change to remote server like "xmpp.jp" if needed
SENSOR_JID = f"sensor@{XMPP_SERVER}"
SENSOR_PASSWORD = "sensor123"


class SensorAgent(Agent):
    """
    SPADE-based sensor agent that monitors environmental conditions 
    and detects disaster events
    """
    
    class PerceptionBehaviour(PeriodicBehaviour):
        """
        Periodic behavior that senses the environment and detects disasters
        """
        
        async def on_start(self):
            """Initialize the environment when behavior starts"""
            self.environment = DisasterEnvironment()
            self.log_file = "logs/LAB2_sensor_logs.txt"
            print(f"\n[{self.agent.jid}] Perception behavior started")
            print(f"[{self.agent.jid}] Monitoring locations: {[loc.name for loc in self.environment.locations]}\n")
        
        async def run(self):
            """Execute perception cycle"""
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            print(f"{'='*80}")
            print(f"[{timestamp}] PERCEPTION CYCLE")
            print(f"{'='*80}\n")
            
            # Update environment state
            self.environment.update_environment()
            
            # Get all percepts
            percepts = self.environment.get_all_percepts()
            
            # Process each location's percept
            for percept in percepts:
                location = percept.location
                
                print(f"Location: {location.name}")
                print(f"  Temperature: {percept.temperature:.1f}°C")
                print(f"  Humidity: {percept.humidity:.1f}%")
                print(f"  Water Level: {percept.water_level:.2f}m")
                print(f"  Visibility: {percept.visibility:.1f}m")
                
                # Check for disasters
                if percept.active_disasters:
                    print(f"  🚨 DISASTERS DETECTED:")
                    for disaster in percept.active_disasters:
                        print(f"     - {disaster.disaster_type.value.upper()}")
                        print(f"       Severity: {disaster.severity.name}")
                        print(f"       Casualties: {disaster.casualties}")
                        print(f"       Infrastructure Damage: {disaster.infrastructure_damage}%")
                        print(f"       Affected Population: {disaster.affected_population}")
                        
                        # Log disaster event
                        self._log_disaster(timestamp, disaster)
                else:
                    print(f"  ✓ No active disasters")
                
                print()
            
            print(f"{'='*80}\n")
        
        def _log_disaster(self, timestamp, disaster):
            """Log disaster events to file"""
            try:
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(f"[{timestamp}] {disaster.location.name} | ")
                    f.write(f"{disaster.disaster_type.value} | ")
                    f.write(f"Severity: {disaster.severity.name} | ")
                    f.write(f"Casualties: {disaster.casualties} | ")
                    f.write(f"Affected: {disaster.affected_population}\n")
            except Exception as e:
                print(f"Error logging disaster: {e}")
    
    async def setup(self):
        """Agent setup - called when agent starts"""
        print(f"\n{'='*80}")
        print(f"SensorAgent Setup")
        print(f"{'='*80}")
        print(f"Agent JID: {self.jid}")
        print(f"Starting perception behavior with 5-second interval")
        print(f"{'='*80}\n")
        
        # Add periodic behavior (runs every 5 seconds)
        b = self.PerceptionBehaviour(period=5)
        self.add_behaviour(b)


async def main():
    """Main entry point for Lab 2"""
    print("\nLAB 2: Perception and Environment Modeling")
    print("Disaster Response & Relief Coordination System\n")
    
    # Configuration info
    print(f"XMPP Configuration:")
    print(f"  Server: {XMPP_SERVER}")
    print(f"  Agent JID: {SENSOR_JID}")
    print(f"  Note: Update XMPP_SERVER variable for remote servers\n")
    
    # Create and start sensor agent
    sensor = SensorAgent(SENSOR_JID, SENSOR_PASSWORD)
    await sensor.start()
    
    print("✓ Sensor agent is running")
    print("Press Ctrl+C to stop\n")
    
    try:
        # Keep agent running
        while sensor.is_alive():
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping sensor agent...")
        await sensor.stop()
        print("✓ Agent stopped successfully\n")


if __name__ == "__main__":
    asyncio.run(main())