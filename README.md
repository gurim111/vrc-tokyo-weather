# vrc-tokyo-weather
Tokyo's current weather as a small JSON file for a VRChat world (VRCStringDownloader).

- `fetch_weather.py` — reads Open-Meteo (no API key) and writes `weather.json`
- `.github/workflows/weather.yml` — runs it every 15 minutes and commits the result
- GitHub Pages (branch `main`, folder `/`) serves `https://gurim111.github.io/vrc-tokyo-weather/weather.json`

Weather data by [Open-Meteo.com](https://open-meteo.com/) (CC BY 4.0).
