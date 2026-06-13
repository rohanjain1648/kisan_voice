"""Weather module using Open-Meteo (free, no API key required)."""
import requests
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
TIMEOUT = 8

WEATHER_CODES = {
    0: "☀️ Clear sky", 1: "🌤️ Mainly clear", 2: "⛅ Partly cloudy", 3: "☁️ Overcast",
    45: "🌫️ Foggy", 48: "🌫️ Icy fog",
    51: "🌦️ Light drizzle", 53: "🌦️ Moderate drizzle", 55: "🌦️ Dense drizzle",
    61: "🌧️ Slight rain", 63: "🌧️ Moderate rain", 65: "🌧️ Heavy rain",
    71: "🌨️ Slight snow", 73: "🌨️ Moderate snow", 75: "🌨️ Heavy snow",
    77: "🌨️ Snow grains",
    80: "🌦️ Slight showers", 81: "🌦️ Moderate showers", 82: "⛈️ Heavy showers",
    85: "🌨️ Slight snow showers", 86: "🌨️ Heavy snow showers",
    95: "⛈️ Thunderstorm", 96: "⛈️ Thunderstorm + hail", 99: "⛈️ Thunderstorm + heavy hail",
}

FARMING_THRESHOLDS = {
    "ideal_temp_min": 20,
    "ideal_temp_max": 32,
    "high_temp": 38,
    "rain_spray_limit": 5,     # mm — avoid spraying if >5mm rain expected
    "irrigation_humidity": 40,  # % — irrigate if humidity < 40%
    "wind_spray_limit": 20,    # km/h — avoid spraying if wind > 20 km/h
}


def _geocode(location: str) -> tuple[float | None, float | None, str]:
    """Returns (lat, lon, display_name)."""
    try:
        resp = requests.get(
            GEOCODING_URL,
            params={"name": location, "count": 3, "language": "en"},
            timeout=TIMEOUT,
        )
        data = resp.json()
        results = data.get("results", [])
        if not results:
            return None, None, location

        # Prefer Indian results
        india = [r for r in results if r.get("country_code") == "IN"]
        best = india[0] if india else results[0]

        name_parts = filter(None, [best.get("name"), best.get("admin2"), best.get("admin1"), best.get("country")])
        display = ", ".join(list(name_parts)[:3])
        return best["latitude"], best["longitude"], display

    except Exception as e:
        logger.warning(f"Geocoding failed for '{location}': {e}")
        return None, None, location


def get_weather(location: str) -> dict:
    """Fetch 7-day weather forecast. Falls back to demo data on error."""
    lat, lon, display_name = _geocode(location)

    if lat is None:
        return _demo_weather(location)

    try:
        resp = requests.get(
            WEATHER_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "current": [
                    "temperature_2m", "relative_humidity_2m", "apparent_temperature",
                    "precipitation", "rain", "weather_code", "wind_speed_10m",
                    "wind_direction_10m", "uv_index",
                ],
                "daily": [
                    "temperature_2m_max", "temperature_2m_min",
                    "precipitation_sum", "rain_sum", "wind_speed_10m_max",
                    "weather_code", "uv_index_max", "sunrise", "sunset",
                ],
                "forecast_days": 7,
                "timezone": "Asia/Kolkata",
            },
            timeout=TIMEOUT,
        )
        data = resp.json()
        return {
            "location": display_name,
            "current": data.get("current", {}),
            "daily": data.get("daily", {}),
            "is_live": True,
            "retrieved_at": datetime.now().strftime("%d %b %Y, %H:%M IST"),
        }
    except Exception as e:
        logger.warning(f"Weather API failed: {e}")
        return _demo_weather(display_name)


def _demo_weather(location: str) -> dict:
    today = datetime.now()
    return {
        "location": location,
        "current": {
            "temperature_2m": 28.5, "relative_humidity_2m": 72,
            "apparent_temperature": 32.0, "precipitation": 0.0,
            "rain": 0.0, "weather_code": 2, "wind_speed_10m": 14,
            "uv_index": 7,
        },
        "daily": {
            "time": [(today + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)],
            "temperature_2m_max": [31, 32, 30, 29, 33, 34, 31],
            "temperature_2m_min": [22, 21, 20, 22, 23, 24, 22],
            "precipitation_sum": [0.0, 2.1, 15.3, 0.0, 0.0, 8.2, 3.1],
            "wind_speed_10m_max": [18, 22, 28, 15, 12, 20, 16],
            "weather_code": [2, 51, 63, 1, 0, 80, 51],
            "uv_index_max": [8, 7, 5, 9, 10, 7, 8],
        },
        "is_live": False,
        "retrieved_at": datetime.now().strftime("%d %b %Y, %H:%M IST") + " (demo data)",
    }


def format_weather_markdown(weather: dict) -> str:
    """Format weather data as a clean Markdown card."""
    c = weather["current"]
    d = weather["daily"]
    live_badge = "🟢 Live" if weather.get("is_live") else "🟡 Demo"

    temp = c.get("temperature_2m", "N/A")
    feels = c.get("apparent_temperature", "N/A")
    humidity = c.get("relative_humidity_2m", "N/A")
    precip = c.get("precipitation", 0)
    wind = c.get("wind_speed_10m", "N/A")
    uv = c.get("uv_index", "N/A")
    condition = WEATHER_CODES.get(c.get("weather_code", 0), "Unknown")

    weekly_rain = sum(d.get("precipitation_sum", [0] * 7))

    # Build forecast rows
    times = d.get("time", [])
    max_t = d.get("temperature_2m_max", ["-"] * 7)
    min_t = d.get("temperature_2m_min", ["-"] * 7)
    rain = d.get("precipitation_sum", [0] * 7)
    codes = d.get("weather_code", [0] * 7)
    day_labels = ["Today", "Tomorrow"] + [
        (datetime.now() + timedelta(days=i)).strftime("%a %d") for i in range(2, 7)
    ]

    forecast_rows = ""
    for i in range(min(7, len(max_t))):
        icon = WEATHER_CODES.get(codes[i] if i < len(codes) else 0, "")[:2]
        forecast_rows += f"| {day_labels[i]} | {icon} | {max_t[i]}° | {min_t[i]}° | {rain[i]:.1f}mm |\n"

    # Farming alerts
    alerts = _generate_farming_alerts(c, d)

    return f"""## 📍 {weather['location']} — {live_badge}
*{weather.get('retrieved_at', '')}*

### Current Conditions
| Metric | Value |
|--------|-------|
| 🌡️ Temperature | {temp}°C (Feels {feels}°C) |
| 💧 Humidity | {humidity}% |
| 🌧️ Rain Now | {precip}mm |
| 💨 Wind | {wind} km/h |
| ☀️ UV Index | {uv} |
| 🌤️ Condition | {condition} |
| 🌦️ 7-Day Rain Total | {weekly_rain:.1f}mm |

### 7-Day Forecast
| Day | | Max | Min | Rain |
|-----|--|-----|-----|------|
{forecast_rows}
{alerts}"""


def _generate_farming_alerts(current: dict, daily: dict) -> str:
    t = FARMING_THRESHOLDS
    alerts = []

    temp = current.get("temperature_2m", 25)
    humidity = current.get("relative_humidity_2m", 60)
    wind = current.get("wind_speed_10m", 0)

    if temp > t["high_temp"]:
        alerts.append("🔴 **Heat Stress Alert**: Irrigate in early morning/evening only. Apply mulch to conserve moisture.")
    elif temp < t["ideal_temp_min"]:
        alerts.append("🔵 **Cold Alert**: Protect seedlings with cover. Delay transplanting.")

    if humidity < t["irrigation_humidity"]:
        alerts.append("💧 **Low Humidity**: Check soil moisture. Drip irrigation recommended today.")

    upcoming_rain = sum(daily.get("precipitation_sum", [0] * 3)[:3])
    if upcoming_rain > 20:
        alerts.append("🌧️ **Heavy Rain Forecast**: Hold off on fertilizer/spray applications this week.")
    elif upcoming_rain < 2:
        alerts.append("☀️ **Dry Spell Ahead**: Plan irrigation for next 3 days.")

    if wind > t["wind_spray_limit"]:
        alerts.append("💨 **High Wind Alert**: Postpone foliar sprays. Risk of spray drift.")

    if not alerts:
        alerts.append("✅ **Conditions Good**: Suitable for normal farming activities today.")

    return "\n### 🚨 Farming Alerts\n" + "\n".join(f"- {a}" for a in alerts)


def get_weather_summary_for_llm(weather: dict) -> str:
    """Compact weather context for the LLM prompt."""
    c = weather["current"]
    d = weather["daily"]
    rain_3d = sum(d.get("precipitation_sum", [0] * 3)[:3])
    return (
        f"Location: {weather['location']} | "
        f"Temp: {c.get('temperature_2m')}°C | "
        f"Humidity: {c.get('relative_humidity_2m')}% | "
        f"Current rain: {c.get('precipitation', 0)}mm | "
        f"Wind: {c.get('wind_speed_10m')} km/h | "
        f"3-day rain forecast: {rain_3d:.1f}mm | "
        f"Condition: {WEATHER_CODES.get(c.get('weather_code', 0), 'clear')}"
    )
