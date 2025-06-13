# app.py
import asyncio, uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from agents import Agent, Runner
from agents.mcp import MCPServerStdio
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# 1️⃣  mount static files **under /static** (no wildcard at "/")
app.mount("/static", StaticFiles(directory="static"), name="static")

# 2️⃣  serve index.html for GET /
@app.get("/", include_in_schema=False)
async def index():
    return FileResponse("static/index.html")

# 3️⃣  MCP + Agent setup (unchanged)
weather_server = MCPServerStdio(
    name="weather",
    params={"command": "python", "args": ["weather_mcp.py"]},
)
agent = None             # lazy-init once

class Msg(BaseModel):
    message: str

async def get_agent():
    global agent
    if agent is None:
        await weather_server.__aenter__()
        agent = Agent(
            name="Weather-Assistant",
            instructions="Use weather tools as needed.",
            mcp_servers=[weather_server],
        )
    return agent

# 4️⃣  the chat endpoint – stays POST /chat
@app.post("/chat")
async def chat(msg: Msg):
    ag = await get_agent()
    res = await Runner.run(starting_agent=ag, input=msg.message)
    return {"answer": res.final_output}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
