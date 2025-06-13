import asyncio
from pprint import pprint
from energy_mcp_nordpool import _fetch_prices

async def main():
    prices = await _fetch_prices("NL", tomorrow=True)
    pprint(prices)

asyncio.run(main())













