# app.py
import os, sys, asyncio
from pathlib import Path
from uuid import uuid4

import os
os.environ["OPENAI_HTTP_CLIENT_TIMEOUT"] = "30"   # seconden
os.environ["OPENAI_HTTP_CLIENT_CONNECT_TIMEOUT"] = "30"   # connect-fase

import openai                       # ← eerst importeren
openai.timeout = 30.0      # of api_request_timeout voor oudere lib
openai.api_request_timeout = 30  # ← werkt op oudere openai-sdk

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from agents import Agent, Runner
from agents.mcp import MCPServerStdio

import logging



os.environ["AGENTS_LOG_LEVEL"] = "DEBUG"   # agent-beslissingen
os.environ["MCP_LOG_LEVEL"] = "DEBUG"      # JSON-RPC tussen client & server

logging.basicConfig(
    level=logging.DEBUG,                   # alles tonen
    format="%(levelname)s %(name)s: %(message)s",
)
# minder ruis van Tornado/uvicorn
logging.getLogger("uvicorn.error").setLevel(logging.INFO)

# 0. .env laden (OpenAI- en Weather-sleutels)
load_dotenv(Path(__file__).with_name(".env"))

# 1. MCP-sub-proces
# app.py  – vervang het bestaande blok
weather_server = MCPServerStdio(
    name="weather",
    params={
        "command": sys.executable,
        "args": [str(Path(__file__).with_name("weather_mcp.py"))],
        "cwd": str(Path(__file__).parent),
        "env": os.environ,
        "timeout_seconds": 30.0,
    },
)

energy_server = MCPServerStdio(
    name="energy",
    params={
        "command": sys.executable,
        "args": [str(Path(__file__).with_name("energy_mcp_nordpool.py"))],
        "cwd":  str(Path(__file__).parent),
        "env":  os.environ,
        "timeout_seconds": 30.0,
    },
)


# 2. Eén agent – hergebruik
agent = Agent(
    name="Weather-Assistant",
   instructions=(
        "Je bent een behulpzame Nederlandse assistent. "
        "Gebruik:\n"
        "• current_weather / forecast voor weer‐vragen.\n"
        "• day_ahead_price / price_forecast voor stroomprijs‐vragen.\n"
        "Combineer deze info wanneer relevant (bijv. advies over wanneer apparaten aan te zetten)."
    ),
    mcp_servers=[weather_server, energy_server],
)

# 3. FastAPI + statische bestanden
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", include_in_schema=False)
async def index():
    return FileResponse("static/index.html")

# 4. Thread-geheugen per sessie via cookie
threads: dict[str, list] = {}      # session-id ➜ chat-thread (list[InputItem])

@app.middleware("http")
async def add_session_cookie(request: Request, call_next):
    sid = request.cookies.get("session-id") or uuid4().hex
    request.state.session_id = sid
    response = await call_next(request)
    response.set_cookie("session-id", sid, httponly=True, max_age=7*24*3600)
    return response

# 5. Chat-endpoint
from pydantic import BaseModel
class Msg(BaseModel):
    message: str

@app.post("/chat")
async def chat(msg: Msg, request: Request):
    sid = request.state.session_id
    thread = threads.get(sid, [])
    logging.debug("▶️  [%s] user: %s", sid[:6], msg.message)

    # voeg nieuwe user-bericht toe aan bestaande thread (of start nieuwe)
    input_items = thread + [{"role": "user", "content": msg.message}]

    # run agent
    result = await Runner.run(agent, input_items)

    # update thread voor volgende beurt
    logging.debug("◀️  [%s] assistant: %s", sid[:6], result.final_output)
    threads[sid] = result.to_input_list()
    return {"answer": result.final_output}

# 6. MCP-server netjes openen/sluiten
@app.on_event("startup")
async def startup():
    await weather_server.__aenter__()
    await energy_server.__aenter__()


@app.on_event("shutdown")
async def shutdown():
    await weather_server.__aexit__(None, None, None)
    await energy_server.__aexit__(None, None, None)


# 7. Start Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
