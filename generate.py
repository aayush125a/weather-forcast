import requests
import pytz
from datetime import datetime
from time import sleep

# ────────────────────────────────────────────────
#  CONFIG
# ────────────────────────────────────────────────

CRYPTO_IDS = {
    "BTC":  "bitcoin",
    "ETH":  "ethereum",
    "SOL":  "solana",
    "SUI":  "sui",
    "AERO": "aerodrome-finance",
}

WEATHER_LOCATIONS = [
    {"flag": "🇳🇵", "country": "Nepal",     "city": "Kathmandu"},
    {"flag": "🇮🇳", "country": "India",     "city": "New Delhi"},
    {"flag": "🇺🇸", "country": "USA",       "city": "New York"},
    {"flag": "🇦🇺", "country": "Australia", "city": "Sydney"},
    {"flag": "🇳🇬", "country": "Nigeria",   "city": "Lagos"},
]

WEATHER_ICON = {
    "sunny": "☀️", "clear": "☀️", "partly cloudy": "⛅",
    "cloudy": "☁️", "overcast": "☁️", "rain": "🌧️",
    "drizzle": "🌦️", "thunder": "⛈️", "snow": "❄️",
    "mist": "🌫️", "fog": "🌫️", "haze": "🌫️",
}

# ────────────────────────────────────────────────
#  FETCH FUNCTIONS
# ────────────────────────────────────────────────

def get_weather(city: str) -> dict | None:
    """Fetch weather from wttr.in — free, no API key needed."""
    for attempt in range(3):
        try:
            r = requests.get(
                f"https://wttr.in/{city}?format=j1",
                timeout=10,
                headers={"User-Agent": "curl/7.68.0"}
            )
            d = r.json()
            cur     = d["current_condition"][0]
            today   = d["weather"][0]
            tmr     = d["weather"][1]
            desc    = cur["weatherDesc"][0]["value"]
            icon    = next((v for k, v in WEATHER_ICON.items() if k in desc.lower()), "🌡️")
            return {
                "desc":       desc,
                "icon":       icon,
                "temp":       cur["temp_C"],
                "feels":      cur["FeelsLikeC"],
                "humidity":   cur["humidity"],
                "wind":       cur["windspeedKmph"],
                "today_hi":   today["maxtempC"],
                "today_lo":   today["mintempC"],
                "today_desc": today["hourly"][4]["weatherDesc"][0]["value"],
                "tmr_hi":     tmr["maxtempC"],
                "tmr_lo":     tmr["mintempC"],
                "tmr_desc":   tmr["hourly"][4]["weatherDesc"][0]["value"],
            }
        except Exception as e:
            print(f"  ⚠ Weather attempt {attempt+1} failed for {city}: {e}")
            sleep(2)
    return None


def get_crypto() -> dict:
    """
    Try CoinGecko public API.
    Falls back to Binance spot prices for BTC/ETH/SOL if CoinGecko fails.
    """
    ids = ",".join(CRYPTO_IDS.values())

    # ── Primary: CoinGecko ─────────────────────
    for attempt in range(3):
        try:
            r = requests.get(
                "https://api.coingecko.com/api/v3/simple/price",
                params={
                    "ids": ids,
                    "vs_currencies": "usd",
                    "include_24hr_change": "true",
                    "include_market_cap": "true",
                },
                timeout=12,
            )
            if r.status_code == 429:
                print(f"  ⏳ Rate limited by CoinGecko, waiting 30s...")
                sleep(30)
                continue
            data = r.json()
            result = {}
            for sym, cg_id in CRYPTO_IDS.items():
                if cg_id in data:
                    price  = data[cg_id].get("usd", 0)
                    change = data[cg_id].get("usd_24h_change") or 0
                    mcap   = data[cg_id].get("usd_market_cap") or 0
                    result[sym] = _fmt(price, change, mcap)
                else:
                    result[sym] = _na()
            print("  ✅ Crypto from CoinGecko")
            return result
        except Exception as e:
            print(f"  ⚠ CoinGecko attempt {attempt+1} failed: {e}")
            sleep(5)

    # ── Fallback: Binance (BTC/ETH/SOL only) ──
    print("  🔁 Falling back to Binance...")
    result = {sym: _na() for sym in CRYPTO_IDS}
    binance_map = {"BTC": "BTCUSDT", "ETH": "ETHUSDT", "SOL": "SOLUSDT"}
    for sym, pair in binance_map.items():
        try:
            ticker = requests.get(
                f"https://api.binance.com/api/v3/ticker/24hr?symbol={pair}",
                timeout=8
            ).json()
            price  = float(ticker["lastPrice"])
            change = float(ticker["priceChangePercent"])
            result[sym] = _fmt(price, change, 0)
        except Exception as e:
            print(f"    ⚠ Binance {pair} failed: {e}")
    return result


def _fmt(price, change, mcap) -> dict:
    arrow = "🟢" if change >= 0 else "🔴"
    sign  = "+" if change >= 0 else ""
    p_str = f"${price:,.4f}" if price < 1 else f"${price:,.2f}"
    if mcap >= 1e9:
        m_str = f"${mcap/1e9:.2f}B"
    elif mcap >= 1e6:
        m_str = f"${mcap/1e6:.1f}M"
    else:
        m_str = "—"
    return {"price": p_str, "change": f"{sign}{change:.2f}%", "mcap": m_str, "arrow": arrow}


def _na() -> dict:
    return {"price": "N/A", "change": "N/A", "mcap": "N/A", "arrow": "⚪"}


# ────────────────────────────────────────────────
#  README BUILDER
# ────────────────────────────────────────────────

def build_readme(crypto: dict, weather_rows: list, utc_now: datetime) -> str:
    ist   = pytz.timezone("Asia/Kolkata")
    ist_t = utc_now.astimezone(ist)
    utc_s = utc_now.strftime("%d %b %Y — %H:%M:%S UTC")
    ist_s = ist_t.strftime("%d %b %Y — %I:%M %p IST")
    day   = ist_t.strftime("%A")

    md = f"""<!-- AUTO-GENERATED — DO NOT EDIT MANUALLY -->
# 📊 Daily Market Dashboard

> 🤖 Auto-updated every day at **9:00 PM IST**

| 🕐 IST | 🌐 UTC |
|--------|--------|
| `{ist_s}` | `{utc_s}` |

---

## 💹 Crypto Prices

| Token | Price | 24h | Market Cap |
|-------|-------|-----|-----------|
"""
    for sym, d in crypto.items():
        md += f"| **{sym}** | `{d['price']}` | {d['arrow']} `{d['change']}` | `{d['mcap']}` |\n"

    md += "\n---\n\n## 🌤️ Weather Forecast\n\n"

    for row in weather_rows:
        loc = row["loc"]
        w   = row["data"]
        md += f"### {loc['flag']} {loc['country']} &mdash; {loc['city']}\n\n"
        if w:
            md += (
                f"> {w['icon']} **{w['desc']}** &nbsp;·&nbsp; "
                f"🌡️ **{w['temp']}°C** *(feels {w['feels']}°C)* &nbsp;·&nbsp; "
                f"💧 {w['humidity']}% humidity &nbsp;·&nbsp; "
                f"🌬️ {w['wind']} km/h\n\n"
            )
            md += "| | Today | Tomorrow |\n|---|---|---|\n"
            md += f"| 🔺 High | {w['today_hi']}°C | {w['tmr_hi']}°C |\n"
            md += f"| 🔻 Low  | {w['today_lo']}°C | {w['tmr_lo']}°C |\n"
            md += f"| ☁️ Condition | {w['today_desc']} | {w['tmr_desc']} |\n\n"
        else:
            md += "> ⚠️ Unavailable right now.\n\n"

    md += f"""---

<sub>📡 Sources: [CoinGecko](https://coingecko.com) · [wttr.in](https://wttr.in) &nbsp;|&nbsp; ⚙️ Powered by GitHub Actions &nbsp;|&nbsp; 🔁 Commits daily at 9 PM IST</sub>
"""
    return md


# ────────────────────────────────────────────────
#  MAIN
# ────────────────────────────────────────────────

if __name__ == "__main__":
    utc_now = datetime.now(pytz.utc)
    print(f"\n🚀 Running at {utc_now.strftime('%Y-%m-%d %H:%M:%S UTC')}\n")

    print("📈 Fetching crypto prices...")
    crypto = get_crypto()
    for sym, d in crypto.items():
        print(f"   {sym}: {d['price']}  {d['change']}")

    print("\n🌤️  Fetching weather...")
    weather_rows = []
    for loc in WEATHER_LOCATIONS:
        print(f"   → {loc['city']}")
        weather_rows.append({"loc": loc, "data": get_weather(loc["city"])})
        sleep(1)   # be polite to wttr.in

    print("\n✍️  Writing README.md...")
    readme = build_readme(crypto, weather_rows, utc_now)
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme)

    print("✅ Done!\n")
