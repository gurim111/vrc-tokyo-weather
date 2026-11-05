"""Fetch Tokyo's current weather from Open-Meteo (no API key) and write weather.json for the VRChat world.
Runs every 15 minutes on GitHub Actions; the JSON is served by GitHub Pages (a VRChat trusted string-loading domain)."""
import json, urllib.request, datetime, math, pathlib

LAT, LON, TZ = 35.6895, 139.6917, "Asia/Tokyo"
URL = ("https://api.open-meteo.com/v1/forecast?latitude=%s&longitude=%s&timezone=%s"
       "&current=temperature_2m,relative_humidity_2m,is_day,precipitation,rain,showers,snowfall,weather_code,cloud_cover,"
       "wind_speed_10m,wind_direction_10m,visibility&daily=sunrise,sunset&forecast_days=1&wind_speed_unit=ms") % (LAT, LON, TZ)

def classify(code, rain, snow, wind):
    """WMO weather code -> (condition, intensity 0..1)."""
    if code in (95, 96, 99): return "thunder", min(1.0, 0.6 + rain / 10.0)
    if code in (71, 73, 75, 77, 85, 86):
        base = {71: 0.35, 73: 0.6, 75: 0.9, 77: 0.3, 85: 0.5, 86: 0.85}[code]
        return ("heavy_snow" if base >= 0.85 or snow >= 2.0 else "snow"), max(base, min(1.0, snow / 3.0))
    if code in (65, 67, 82): return "heavy_rain", max(0.85, min(1.0, rain / 12.0))
    if code in (61, 63, 66, 80, 81): return "rain", max({61: 0.35, 63: 0.6, 66: 0.45, 80: 0.4, 81: 0.65}[code], min(1.0, rain / 8.0))
    if code in (51, 53, 55, 56, 57): return "drizzle", {51: 0.15, 53: 0.25, 55: 0.35, 56: 0.2, 57: 0.3}[code]
    if code in (45, 48): return "fog", 0.7
    if code == 3: return "cloudy", 0.9
    if code in (1, 2): return "partly_cloudy", 0.4 if code == 1 else 0.6
    return "clear", 0.0

def hours(t):  # "2026-11-05T06:05" -> 6.083
    hh, mm = t.split("T")[1].split(":")[:2]; return round(int(hh) + int(mm) / 60.0, 3)

def main():
    with urllib.request.urlopen(URL, timeout=30) as r: d = json.load(r)
    c = d["current"]; daily = d["daily"]
    rain = (c.get("rain") or 0) + (c.get("showers") or 0); snow = c.get("snowfall") or 0
    cond, inten = classify(int(c["weather_code"]), rain, snow, c.get("wind_speed_10m") or 0)
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
    out = {
        "city": "Tokyo", "updated": now.strftime("%Y-%m-%dT%H:%M+09:00"), "observed": c["time"],
        "code": int(c["weather_code"]), "cond": cond, "intensity": round(inten, 3),
        "temp": c.get("temperature_2m"), "humidity": c.get("relative_humidity_2m"), "cloud": c.get("cloud_cover"),
        "precip": c.get("precipitation"), "rain": round(rain, 2), "snowfall": snow,
        "wind": c.get("wind_speed_10m"), "wind_dir": c.get("wind_direction_10m"), "visibility": c.get("visibility"),
        "is_day": int(c.get("is_day") or 0),
        "sunrise": daily["sunrise"][0].split("T")[1], "sunset": daily["sunset"][0].split("T")[1],
        "sunrise_h": hours(daily["sunrise"][0]), "sunset_h": hours(daily["sunset"][0]),
        "source": "Open-Meteo.com (CC BY 4.0)"}
    pathlib.Path("weather.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=1))

if __name__ == "__main__": main()
