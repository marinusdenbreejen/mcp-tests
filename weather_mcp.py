# weather_mcp.py
import logging, os, httpx
from pathlib import Path
from typing import Any

# MCP import – choose the one matching your version
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# ────────────────────────────────────────────────
# 1. Load .env that sits next to this script
load_dotenv(Path(__file__).with_name(".env"))

# 2. Basic logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

# 3. Keys / constants
API_KEY = os.getenv("WEATHER_API_KEY")
if not API_KEY:
    logging.error("WEATHER_API_KEY is not set – check your .env file")
    raise SystemExit(1)

BASE = "https://api.weatherapi.com/v1"   # HTTPS!

logging.info("WEATHER_API_KEY starts with %s…", API_KEY[:6])

# ────────────────────────────────────────────────
# 4. MCP setup
mcp = FastMCP("weather")

async def _fetch(endpoint: str, **params) -> dict[str, Any]:
    params["key"] = API_KEY
    url = f"{BASE}/{endpoint}"
    logging.debug("🌐 GET %s  %s", url, params)
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.get(url, params=params)
        logging.debug("✅ %s %s", r.status_code, url)
        r.raise_for_status()
        return r.json()

@mcp.tool()
async def current_weather(location: str) -> str:
    """Current conditions for a city, lat/long or postal code."""
    d = await _fetch("current.json", q=location, aqi="no")
    c, loc = d["current"], d["location"]
    return (f"{loc['name']}, {loc['country']} — {loc['localtime']}:\n"
            f"{c['temp_c']} °C (feels {c['feelslike_c']} °C), "
            f"{c['condition']['text']}. Wind {c['wind_kph']} kph {c['wind_dir']}, "
            f"humidity {c['humidity']} %.")

@mcp.tool()
async def forecast(location: str, days: int = 3) -> str:
    """Daily forecast (1–10 days)."""
    days = max(1, min(days, 10))
    d = await _fetch("forecast.json", q=location, days=days, aqi="no", alerts="no")
    lines = []
    for fd in d["forecast"]["forecastday"]:
        day = fd["day"]
        lines.append(f"{fd['date']}: {day['avgtemp_c']} °C "
                     f"(min {day['mintemp_c']} ° / max {day['maxtemp_c']} °) – "
                     f"{day['condition']['text']}, rain {day['daily_chance_of_rain']} %.")
    return "\n".join(lines)

# ────────────────────────────────────────────────
if __name__ == "__main__":
    logging.info("Weather MCP server waiting for client …")
    mcp.run(transport="stdio")
