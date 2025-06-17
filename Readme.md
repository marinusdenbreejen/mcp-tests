# 🧪 mcp‑tests

Repository with test setup for the MCP-based Weather + Energy Assistant.

## 🚀 Contents

- `app.py` – FastAPI server integrating OpenAI and MCP servers for weather and energy APIs.  
- `weather_mcp.py` – Standard MCP subserver for weather data (current + forecast).  
- `energy_mcp_nordpool.py` – MCP subserver for Nord Pool day-ahead and hourly forecast prices.  
- `test.py`, `test2.py` – Scripts to test the Nord Pool fetcher and MCP components outside the LLM.

## 🔧 Installation

1. Clone the repo:
   ```bash
   git clone https://github.com/marinusdenbreejen/mcp-tests.git
   cd mcp-tests
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   .venv\Scripts\activate     # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *Make sure your `.env` contains:*  
   ```
   OPENAI_API_KEY=...
   WEATHER_API_KEY=...
   ```

## 🧩 Usage

Start the app with:
```bash
python app.py
```
FastAPI will then run locally at http://127.0.0.1:8000.

### Tests

- Fetch only energy prices without LLM:
  ```bash
  python test2.py
  ```
- Test MCP server tooling separately:
  ```bash
  python test.py
  ```

## 📚 Structure

- **`_fetch_prices()`** in `energy_mcp_nordpool.py`: fetches today/tomorrow prices.
- **`day_ahead_price`**: average day price.
- **`price_forecast`**: cheapest and most expensive hour for the coming X hours.

## 🧠 Further

- Add Nord Pool tomorrow option to the `day_ahead_price` tool.
- Combine with weather data for smart timing advice.
- Add extra MCP tools, e.g., tariff data, energy saving tips.

---

**Author**: Marinus den Breejen  
Repository: `mcp-tests`
