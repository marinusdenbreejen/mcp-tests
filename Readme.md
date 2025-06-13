# 🧪 mcp‑tests

Repository met test‑setup voor de MCP‑gebaseerde Weather + Energy Assistant.

## 🚀 Inhoud

- `app.py` – FastAPI‑server met integratie van OpenAI en MCP‑servers voor weer- en energie-API’s.  
- `weather_mcp.py` – Standaard MCP‑subserver voor weerdata (current + forecast).  
- `energy_mcp_nordpool.py` – MCP‑subserver voor Nord Pool day‑ahead en uur‑forecast prijzen.  
- `test.py`, `test2.py` – Scripts om de Nord Pool‑fetcher en MCP‑componenten buiten LLM te testen.

## 🔧 Installatie

1. Clone de repo:
   ```bash
   git clone https://github.com/marinusdenbreejen/mcp-tests.git
   cd mcp-tests
   ```
2. Maak en activeer virtuele omgeving:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   .venv\Scripts\activate     # Windows
   ```
3. Installeer dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *Zorg dat je in `.env` hebt:*  
   ```
   OPENAI_API_KEY=...
   WEATHER_API_KEY=...
   ```

## 🧩 Gebruik

Start de app via:
```bash
python app.py
```
Dan draait FastAPI lokaal op http://127.0.0.1:8000.

### Tests

- Haal alleen energie-prijzen op zonder LLM:
  ```bash
  python test2.py
  ```
- Test MCP‑server tooling separat:
  ```bash
  python test.py
  ```

## 📚 Structuur

- **`_fetch_prices()`** in `energy_mcp_nordpool.py`: haalt today/tomorrow prijzen op.
- **`day_ahead_price`**: gemiddelde dagprijs.
- **`price_forecast`**: goedkoopste en duurste uur voor komende X uur.

## 🧠 Verder

- Voeg Nord Pool tomorrow-optie toe aan `day_ahead_price` tool.
- Combineer met weer-data voor slimme timing advies.
- Voeg extra MCP‑tools toe, bijvoorbeeld tariefdata, energiebesparingstips.

---

**Auteur**: Marinus den Breejen  
Repository: `mcp-tests`
