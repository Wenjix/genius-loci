from spoon_ai.agents.toolcall import ToolCallAgent
from spoon_ai.tools import ToolManager
from spoon_ai.tools.base import BaseTool
from spoon_ai.chat import ChatBot
from pydantic import Field
import aiohttp
import asyncio

class SmartWeatherTool(BaseTool):
    name: str = "smart_weather"
    description: str = "Get weather and outfit suggestions for a city."
    parameters: dict = {
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "City name"}
        },
        "required": ["city"]
    }

    async def execute(self, city: str) -> str:
        geocode_url = f"https://nominatim.openstreetmap.org/search?q={city}&format=json&limit=1"
        async with aiohttp.ClientSession() as session:
            async with session.get(geocode_url) as resp:
                if resp.status != 200:
                    return f"Failed to get geocode, status: {resp.status}"
                geocode_data = await resp.json()
        if not geocode_data:
            return f"Unable to find geographic information for {city}"
        lat = geocode_data[0]["lat"]
        lon = geocode_data[0]["lon"]
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&timezone=auto"
        )
        async with aiohttp.ClientSession() as session:
            async with session.get(weather_url) as resp:
                if resp.status != 200:
                    return f"Failed to get weather, status: {resp.status}"
                weather_data = await resp.json()
        current_weather = weather_data.get("current_weather", {})
        temperature = current_weather.get("temperature")
        if temperature is None:
            outfit = "No temperature available"
        elif temperature < 5:
            outfit = "Wear a down jacket or thick coat"
        elif 5 <= temperature < 15:
            outfit = "A coat or jacket is recommended"
        elif 15 <= temperature < 25:
            outfit = "Long sleeves or a light jacket are recommended"
        else:
            outfit = "Hot weather, short sleeves recommended"
        return (
            f"City: {city}\n"
            f"Temperature: {temperature}°C\n"
            f"Outfit: {outfit}\n"
        )

class MyInfoAgent(ToolCallAgent):
    name: str = "my_info_agent"
    description: str = (
        "Smart assistant that provides current weather and outfit suggestions"
    )
    system_prompt: str = (
        "You are a helpful assistant with access to tools. Use tools when needed and answer clearly."
    )
    next_step_prompt: str = (
        "Decide next action based on prior results."
    )
    max_steps: int = 5
    available_tools: ToolManager = Field(default_factory=lambda: ToolManager([
        SmartWeatherTool(),
    ]))