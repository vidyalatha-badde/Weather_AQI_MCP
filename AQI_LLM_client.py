import asyncio
import os
from dotenv import load_dotenv
from fastmcp import Client

class AQIAgent:

    def __init__(self, weather_url: str, aqi_server_url: str, llm_server_url: str):
        self.weather_url = weather_url
        self.aqi_server_url = aqi_server_url
        self.llm_server_url = llm_server_url

    async def get_weather(self, location: str) -> str:
        async with Client(f"{self.weather_url}/sse") as client:
            return await client.call_tool("get_weather", {"location": location})

    async def get_aqi_report(self, location: str) -> str:
        """Call AQI MCP server tool to get AQI report."""
        async with Client(f"{self.aqi_server_url}/sse") as client:
            result = await client.call_tool("get_aqi", {"location": location})
            return self._extract_text(result)

    async def get_health_recommendations(self, weather_report: str, aqi_report: str) -> str:
        """Call LLM MCP server tool to get health guidance."""
        async with Client(f"{self.llm_server_url}/sse") as client:
            result = await client.call_tool("safety_guidelines", {"weather_report": weather_report , "aqi_report": aqi_report})
            return self._extract_text(result)

    def _extract_text(self, result) -> str:
        """Helper to extract plain text from MCP result (list or single object)."""
        if isinstance(result, list):
            return "\n".join(block.text for block in result if hasattr(block, "text"))
        elif hasattr(result, "text"):
            return result.text
        return str(result)

async def main():
    agent = AQIAgent("http://localhost:8000" , "http://localhost:8003", "http://localhost:8004")

    while True:
        location = input("\n📍 Enter location to check AQI (or 'exit' to quit): ").strip()
        if location.lower() == "exit":
            print("👋 Exiting AQI Assistant.")
            break

        print("\n🌫️ Fetching Weather & AQI data...")
        try:
                   
            weather_raw = await agent.get_weather(location)
            weather_report = weather_raw[0].text if isinstance(weather_raw, list) else str(weather_raw)
            print("\n📡 Weather Report:\n", weather_report)
            
            aqi_report = await agent.get_aqi_report(location)
            print(f"\n📊 AQI Report for '{location}':\n{aqi_report}")

            print("\n💡 Getting health precautions...")
            recommendations = await agent.get_health_recommendations(weather_report, aqi_report)
            print("\n✅ Health & Safety Advice:\n", recommendations)
        except Exception as e:
            print("❌ An error occurred:", str(e))

if __name__ == "__main__":
    asyncio.run(main())
