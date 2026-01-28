from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour
from datetime import datetime
import random

class DisasterEnviroment:
    def __init__(self):
        self.zones = ["Zone A", "Zone B", "Zone C", "Zone D"]

    def get_conditon(self, zone):
        return {
            "temperature": random.randint(20, 40),
            "humidity": random.randint(30, 100),
            "visibility": random.randint(0, 10),
            "severity": random.choice(["LOW", "MEDIUM", "HIGH", "CRITICAL"]),
        }


class SensorAgent(Agent):
    class PerceptionBehaviour(PeriodicBehaviour):
        async def run(self):
            env = DisasterEnviroment()

            for zone in env.zones:
                conditions = env.get_conditon(zone)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                print(f"[{timestamp}] {zone}: Temp={conditions['temperature']}°C, Humidity={conditions['humidity']}%, Visibility={conditions['visibility']}%, Severity={conditions['severity']}")


                with open("disaster_events.log", "a") as f:
                    f.write(f"[{timestamp}] {zone}: Temp={conditions['temperature']}°C, Humidity={conditions['humidity']}%, Visibility={conditions['visibility']}%, Severity={conditions['severity']}\n")

    async def setup(self):
        print("SensorAgent starting perception...")
        b = self.PerceptionBehaviour(period="5")
        self.add_behaviour(b)

if __name__ == "__main__":
    sensor = SensorAgent("sensor@localhost", "1234")
    sensor.start()

    try:
        while sensor.is_alive():
            asyncio.sleep(1)
    except KeyboardInterrupt:
        sensor.stop()   
    


            