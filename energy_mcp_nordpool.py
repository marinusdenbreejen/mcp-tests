# energy_mcp_nordpool.py
import logging, asyncio, pytz
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict

from nordpool.elspot import Prices
from dateutil import tz
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# ───────────────────────────────
load_dotenv(Path(__file__).with_name(".env"))  # optioneel

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
mcp = FastMCP("energy")
spot = Prices()

NL_TZ = tz.gettz("Europe/Amsterdam")

async def _fetch_prices(area: str, tomorrow: bool = False) -> Dict[datetime, float]:
    """Haal Nord Pool spotprijzen op en filter op vandaag of morgen."""
    loop = asyncio.get_running_loop()
    data = await loop.run_in_executor(None, lambda: spot.fetch(areas=[area]))

    target_date = datetime.now(tz=NL_TZ).date()
    if tomorrow:
        target_date += timedelta(days=1)

    prices = {}
    for row in data["areas"][area]["values"]:
        ts_local = row["start"].astimezone(NL_TZ)
        if ts_local.date() != target_date:
            continue
        price_eur_mwh = row["value"]
        if price_eur_mwh is None:
            continue
        prices[row["start"]] = round(price_eur_mwh / 1000, 4)  # €/kWh
    return prices


@mcp.tool()
async def day_ahead_price(area_code: str = "NL", tomorrow: bool = False) -> str:
    """Gemiddelde Nord Pool dagprijs (€/kWh) voor een gebied (vandaag of morgen)."""
    prices = await _fetch_prices(area_code, tomorrow=tomorrow)
    if not prices:
        return f"Geen Nord Pool-prijzen voor {area_code} {'morgen' if tomorrow else 'vandaag'} gevonden."
    vals = list(prices.values())
    avg, low, high = map(lambda v: round(v, 4), (sum(vals)/len(vals), min(vals), max(vals)))
    dag = "morgen" if tomorrow else "vandaag"
    return (f"Nord Pool dagprijs {area_code} ({dag}): gem {avg} €/kWh "
            f"(laag {low}, hoog {high}).")


@mcp.tool()
async def price_forecast(area_code: str = "NL", hours: int = 6, tomorrow: bool = False) -> str:
    """Goedkoopste & duurste uur in komende X uur (1–24) voor een gebied (vandaag of morgen)."""
    hours = max(1, min(hours, 24))
    prices = await _fetch_prices(area_code, tomorrow=tomorrow)
    now = datetime.utcnow().replace(minute=0, second=0, microsecond=0, tzinfo=pytz.UTC)
    fut = {t: v for t, v in prices.items() if t >= now}
    selected = dict(list(fut.items())[:hours])
    if not selected:
        return f"Geen prijsdata beschikbaar {'morgen' if tomorrow else 'in dit tijdvenster'}."
    best = min(selected, key=selected.get)
    worst = max(selected, key=selected.get)
    dag = "morgen" if tomorrow else "vandaag"
    return (f"{dag.capitalize()} komende {hours} u in {area_code}: goedkoopst {best.astimezone(NL_TZ):%H}:00 "
            f"({selected[best]} €/kWh), duurst {worst.astimezone(NL_TZ):%H}:00 "
            f"({selected[worst]} €/kWh).")


if __name__ == "__main__":
    logging.info("⚡ Nord Pool MCP wacht op client …")
    mcp.run(transport="stdio")
