# chat_agent.py
import os, asyncio
from agents import Agent, Runner
from agents.mcp import MCPServerStdio   # docs: see MCPServerStdio class :contentReference[oaicite:2]{index=2}

async def main():
    weather = MCPServerStdio(
        name="weather",
        params={"command": "python", "args": ["weather_mcp.py"]},
    )
    async with weather as ws:
        agent = Agent(
            name="Weather-Assistant",
            instructions=(
                "You are a helpful assistant. "
                "Call the weather tools whenever users ask about weather."
            ),
            mcp_servers=[ws],
        )
        while True:
            user = input("You > ")
            if user.lower() in {"exit", "quit"}:
                break
            result = await Runner.run(starting_agent=agent, input=user)
            print("AI  > " + result.final_output + "\n")

if __name__ == "__main__":
    asyncio.run(main())
