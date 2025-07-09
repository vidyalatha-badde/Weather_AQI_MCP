# weather_server.py

from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather", host="0.0.0.0", port=8000)

GEOCODE_API = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_API = "https://api.open-meteo.com/v1/forecast"

@mcp.tool()
async def get_weather(location: str) -> str:
    """
    Retrieve the current weather information for a given city or country.

    This function performs two steps:
      1. Uses the Open-Meteo Geocoding API to find the latitude and longitude
         of the specified location.
      2. Uses the Open-Meteo Weather API to fetch the current weather forecast
         for those coordinates.

    The returned weather report includes:
      - Location name and country
      - Coordinates (latitude and longitude)
      - Current temperature (°C)
      - Wind speed (km/h)

    Args:
        location (str): The name of the city or country to get weather data for.

    Returns:
        str: A formatted string containing the location details and current weather.
             If the location is not found or weather data is unavailable,
             an appropriate error message is returned instead.
    """
    # Step 1: Geocoding to get lat/lon
    geo_url = f"{GEOCODE_API}?name={location}&count=1&language=en&format=json"
    async with httpx.AsyncClient() as client:
        geo_response = await client.get(geo_url)
        geo_data = geo_response.json()

    if "results" not in geo_data or not geo_data["results"]:
        return f"❌ Location '{location}' not found."

    result = geo_data["results"][0]
    lat = result["latitude"]
    lon = result["longitude"]
    name = result["name"]
    country = result.get("country", "Unknown")

    # Step 2: Get weather forecast
    forecast_url = (
        f"{WEATHER_API}?latitude={lat}&longitude={lon}"
        "&current_weather=true&timezone=auto"
    )
    async with httpx.AsyncClient() as client:
        weather_response = await client.get(forecast_url)
        weather_data = weather_response.json()

    if "current_weather" not in weather_data:
        return f"❌ Weather data not available for '{name}, {country}'."

    current = weather_data["current_weather"]
    temp = current.get("temperature", "N/A")
    wind = current.get("windspeed", "N/A")

    return (
        f"📍 Location: {name}, {country}\n"
        f"🗺️ Coordinates: {lat}, {lon}\n"
        f"🌡️ Temperature: {temp}°C\n"
        f"💨 Wind Speed: {wind} km/h"
    )

if __name__ == "__main__":
    mcp.run("sse")
