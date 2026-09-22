# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types


import json
import urllib.parse
import urllib.request


def get_weather(query: str) -> str:
    """Gets real-time weather information for any queried location using Open-Meteo API.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the real-time weather information for the queried location.
    """
    try:
        encoded_query = urllib.parse.quote(query)
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={encoded_query}&count=1&language=en&format=json"

        req = urllib.request.Request(geo_url, headers={"User-Agent": "ADK-Weather-Agent/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            geo_data = json.loads(resp.read().decode())

        if not geo_data.get("results"):
            return f"Could not find location information for '{query}'."

        loc = geo_data["results"][0]
        lat, lon = loc["latitude"], loc["longitude"]
        city_name = loc.get("name", query)
        country = loc.get("country", "")
        location_label = f"{city_name}, {country}" if country else city_name

        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        req_w = urllib.request.Request(weather_url, headers={"User-Agent": "ADK-Weather-Agent/1.0"})
        with urllib.request.urlopen(req_w, timeout=5) as resp_w:
            weather_data = json.loads(resp_w.read().decode())

        cw = weather_data.get("current_weather", {})
        temp_c = cw.get("temperature")
        temp_f = round(temp_c * 9 / 5 + 32, 1) if temp_c is not None else "N/A"
        wind_speed = cw.get("windspeed")

        wcode = cw.get("weathercode", 0)
        conditions = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Foggy",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            71: "Slight snow fall",
            73: "Moderate snow fall",
            75: "Heavy snow fall",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            95: "Thunderstorm",
        }
        condition_text = conditions.get(wcode, "Clear/Sunny")

        return f"Real-time weather in {location_label}: {temp_c}°C ({temp_f}°F), Condition: {condition_text}, Wind speed: {wind_speed} km/h."
    except Exception as e:
        return f"Error fetching real-time weather for '{query}': {str(e)}"


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        query: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    q = query.lower()
    timezones = {
        "san francisco": "America/Los_Angeles",
        "sf": "America/Los_Angeles",
        "new york": "America/New_York",
        "ny": "America/New_York",
        "delhi": "Asia/Kolkata",
        "london": "Europe/London",
        "tokyo": "Asia/Tokyo",
    }

    tz_identifier = None
    for city, tz_name in timezones.items():
        if city in q:
            tz_identifier = tz_name
            break

    if not tz_identifier:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


from a2ui.schema.manager import A2uiSchemaManager
from a2ui.basic_catalog.provider import BasicCatalog

from google.adk.agents.callback_context import CallbackContext
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from app.destination_tools import (
    search_destinations,
    add_destination,
    save_favorite_destination,
    get_favorite_destinations,
    get_live_destination_weather,
    consult_travel_guide,
    generate_destination_image,
)
from app.a2ui_utils import a2ui_callback


async def generate_memories_callback(callback_context: CallbackContext):
    """Callback to extract durable user facts and travel preferences into Vertex AI Memory Bank."""
    await callback_context.add_session_to_memory()
    return None


schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are the Travel Destination Explorer assistant. You help users discover amazing travel "
        "destinations and plan trips. You remember user travel preferences across sessions — such as "
        "budget range, preferred climate (tropical, temperate, cold), travel style (adventure, relaxation, culture), "
        "and whether they travel solo or with family — and use them to personalize your recommendations. "
        "You also have access to a Firestore destination database, live weather, document retrieval, destination image generation, "
        "and Python code execution in a secure sandbox."
    ),
    workflow_description=(
        "Analyze the user request, call function tools when appropriate (search_destinations, add_destination, "
        "save_favorite_destination, get_favorite_destinations, get_live_destination_weather, consult_travel_guide, "
        "generate_destination_image, or code execution), and return structured UI when presenting destinations, options, or facts."
    ),
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        '{"Image": {"url": {"literalString": "https://..."}}}. Never point an '
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    code_executor=AgentEngineSandboxCodeExecutor(),
    instruction=instruction,
    tools=[
        PreloadMemoryTool(),
        get_current_time,
        search_destinations,
        add_destination,
        save_favorite_destination,
        get_favorite_destinations,
        get_live_destination_weather,
        consult_travel_guide,
        generate_destination_image,
    ],
    after_model_callback=a2ui_callback,
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)

