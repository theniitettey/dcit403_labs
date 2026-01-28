from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
import asyncio


class BasicAgent(Agent):
    class MyBehaviour(CyclicBehaviour):
        async def run(self):
            print(f"[{self.agent.jid}] Behaviour cycle running...")
            await asyncio.sleep(2)

            if self.counter >= 5:
                await self.agent.stop()
            self.counter += 1
        
        async def on_start(self):
            self.counter = 0
            print(f"[{self.agent.jid}] Behaviour starting...")
    
    async def setup(self):
        print(f"[{self.jid}] Agent setup completed")
        b = self.MyBehaviour()
        self.add_behaviour(b)


if __name__ == "__main__":
    agent = BasicAgent("basic_agent@localhost", "1234")
    
    future = agent.start()
    future.result()

    print("Agent is running. Press Ctrcl+C to stop")

    try:
        while agent.is_alive():
            asyncio.sleep(1)
    except KeyboardInterrupt:
        agent.stop()    