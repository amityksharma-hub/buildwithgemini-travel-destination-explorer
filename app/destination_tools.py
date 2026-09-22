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
from typing import Optional
from google.cloud import firestore

# Hardcode project ID as a string to avoid runtime project number resolution issue on Agent Platform
PROJECT_ID = "qwiklabs-gcp-03-61708ee92f67"


def _get_firestore_client() -> firestore.Client:
    """Returns a Firestore client initialized with hardcoded project ID string."""
    return firestore.Client(project=PROJECT_ID)


def search_destinations(
    budget_level: Optional[str] = None,
    climate: Optional[str] = None,
    country: Optional[str] = None,
) -> str:
    """Search travel destinations stored in the Firestore database.

    Args:
        budget_level: Optional budget tier filter ('budget', 'mid-range', 'luxury').
        climate: Optional climate category filter ('beach', 'mountain', 'city', 'desert').
        country: Optional country filter (e.g. 'Indonesia', 'Japan', 'India').

    Returns:
        A formatted list of matching travel destinations from Firestore.
    """
    try:
        db = _get_firestore_client()
        query = db.collection("destinations")

        if budget_level:
            query = query.where("budget_level", "==", budget_level.lower())
        if climate:
            query = query.where("climate", "==", climate.lower())
        if country:
            query = query.where("country", "==", country)

        docs = list(query.stream())
        if not docs:
            return "No destinations found matching your criteria in the database."

        results = []
        for doc in docs:
            data = doc.to_dict()
            results.append(
                f"- **{data.get('name')}** ({data.get('country')}):\n"
                f"  - Description: {data.get('description')}\n"
                f"  - Climate: {data.get('climate')}\n"
                f"  - Budget Level: {data.get('budget_level')}\n"
                f"  - Best Season: {data.get('best_season')}"
            )
        return "\n\n".join(results)
    except Exception as e:
        return f"Error searching destinations in Firestore: {str(e)}"


def add_destination(
    name: str,
    country: str,
    description: str,
    best_season: str,
    budget_level: str,
    climate: str,
) -> str:
    """Add a new destination to the Firestore database.

    Args:
        name: Name of the destination city or spot (e.g. 'Santorini').
        country: Country where the destination is located (e.g. 'Greece').
        description: Summary of sights, culture, and highlights.
        best_season: Recommended months/season to visit (e.g. 'May to October').
        budget_level: Budget tier ('budget', 'mid-range', or 'luxury').
        climate: Primary climate category ('beach', 'mountain', 'city', or 'desert').

    Returns:
        Confirmation message that the destination was stored in Firestore.
    """
    try:
        db = _get_firestore_client()
        doc_id = name.lower().replace(" ", "_")
        dest_data = {
            "name": name,
            "country": country,
            "description": description,
            "best_season": best_season,
            "budget_level": budget_level.lower(),
            "climate": climate.lower(),
        }
        db.collection("destinations").document(doc_id).set(dest_data)
        return f"Successfully added '{name}' ({country}) to the destinations database!"
    except Exception as e:
        return f"Error adding destination '{name}' to Firestore: {str(e)}"


def save_favorite_destination(destination_name: str, user_id: str = "default_user") -> str:
    """Save a destination to a user's favorites list in Firestore.

    Args:
        destination_name: Name of the destination to save.
        user_id: Unique identifier for the user (defaults to 'default_user').

    Returns:
        Confirmation message that the destination was saved to favorites.
    """
    try:
        db = _get_firestore_client()
        doc_id = f"{user_id}_{destination_name.lower().replace(' ', '_')}"
        fav_data = {
            "user_id": user_id,
            "destination_name": destination_name,
            "saved_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
        db.collection("favorites").document(doc_id).set(fav_data)
        return f"Successfully saved '{destination_name}' to favorites for user '{user_id}'!"
    except Exception as e:
        return f"Error saving favorite destination: {str(e)}"


def get_favorite_destinations(user_id: str = "default_user") -> str:
    """Retrieve the full list of favorite destinations for a user from Firestore.

    Args:
        user_id: Unique identifier for the user (defaults to 'default_user').

    Returns:
        Formatted list of user's favorite destinations.
    """
    try:
        db = _get_firestore_client()
        docs = list(
            db.collection("favorites").where("user_id", "==", user_id).stream()
        )
        if not docs:
            return f"No favorite destinations found for user '{user_id}'."

        favorites = [
            doc.to_dict().get("destination_name")
            for doc in docs
            if doc.to_dict().get("destination_name")
        ]
        return f"Favorite destinations for '{user_id}': " + ", ".join(favorites)
    except Exception as e:
        return f"Error retrieving favorite destinations: {str(e)}"


WEATHER_CODES = {
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
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


def get_live_destination_weather(city_name: str) -> str:
    """Fetch live current weather for any destination using the Open-Meteo API.

    Args:
        city_name: Name of the destination city or spot (e.g. 'Kyoto', 'Bali', 'Goa', 'Paris').

    Returns:
        A formatted summary of current weather including temperature (°C), wind speed (km/h), and weather condition.
    """
    import urllib.parse
    import urllib.request
    import json

    try:
        # 1. Geocode city name to latitude & longitude
        encoded_city = urllib.parse.quote(city_name)
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={encoded_city}&count=5&language=en&format=json"

        req_geo = urllib.request.Request(geo_url, headers={"User-Agent": "Antigravity/1.0"})
        with urllib.request.urlopen(req_geo, timeout=10) as resp_geo:
            geo_data = json.loads(resp_geo.read().decode("utf-8"))

        results = geo_data.get("results")
        if not results:
            return f"Could not find coordinates for destination '{city_name}'."

        # Pick match with highest population or exact name match
        location = max(results, key=lambda x: (x.get("name", "").lower() == city_name.lower(), x.get("population", 0)))
        name = location.get("name", city_name)
        country = location.get("country", "")
        lat = location.get("latitude")
        lon = location.get("longitude")

        # 2. Fetch current weather for coordinates
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        req_w = urllib.request.Request(weather_url, headers={"User-Agent": "Antigravity/1.0"})
        with urllib.request.urlopen(req_w, timeout=10) as resp_w:
            weather_data = json.loads(resp_w.read().decode("utf-8"))

        current = weather_data.get("current_weather", {})
        temp = current.get("temperature")
        wind = current.get("windspeed")
        code = current.get("weathercode", 0)
        condition = WEATHER_CODES.get(code, f"Weather code {code}")

        country_str = f", {country}" if country else ""
        return (
            f"Current weather for {name}{country_str}:\n"
            f"- Condition: {condition}\n"
            f"- Temperature: {temp}°C\n"
            f"- Wind Speed: {wind} km/h"
        )
    except Exception as e:
        return f"Error fetching live weather for '{city_name}': {str(e)}"


def consult_travel_guide(query: str) -> str:
    """Search the travel guide document corpus for historical notes, herbal facts, plant descriptions, or local travel lore.

    Args:
        query: What to look up (a plant, ailment, travel detail, or historical note).

    Returns:
        Relevant passages retrieved from the document corpus.
    """
    import os
    from vertexai.preview import rag
    import vertexai

    passages = []
    corpus_name = "projects/qwiklabs-gcp-03-61708ee92f67/locations/us-west1/ragCorpora/4611686018427387904"
    try:
        vertexai.init(project="qwiklabs-gcp-03-61708ee92f67", location="us-west1")
        resp = rag.retrieval_query(
            text=query,
            rag_resources=[rag.RagResource(rag_corpus=corpus_name)],
            rag_retrieval_config=rag.RagRetrievalConfig(top_k=5),
        )
        contexts = getattr(resp.contexts, "contexts", [])
        passages = [c.text.strip() for c in contexts if getattr(c, "text", "").strip()]
    except Exception:
        pass

    # Fallback to local indexed document pg49513.txt if vector search returns empty
    if not passages:
        possible_paths = [
            os.path.join(os.path.dirname(__file__), "pg49513.txt"),
            os.path.join(os.path.dirname(__file__), "..", "pg49513.txt"),
            os.path.join(os.getcwd(), "pg49513.txt"),
            os.path.join(os.getcwd(), "app", "pg49513.txt"),
            "/app/pg49513.txt",
        ]
        content = ""
        for p in possible_paths:
            if os.path.exists(p):
                try:
                    with open(p, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    if content:
                        break
                except Exception:
                    pass
        if content:
            terms = [t.lower() for t in query.split() if len(t) > 3]
            paras = [p.strip() for p in content.split("\n\n") if len(p.strip()) > 40]
            matches = [p for p in paras if any(t in p.lower() for t in terms)]
            passages = matches[:3]


    return "\n\n---\n\n".join(passages) or "No relevant passage found in travel guide."



from google.adk.tools import ToolContext


def generate_destination_image(prompt: str, tool_context: ToolContext) -> str:
    """Generates an image for a travel destination using Gemini Flash Lite Image model, saves it to Playground Artifacts, and uploads to GCS.

    Args:
        prompt: Detailed visual prompt describing the travel destination scene to generate.
        tool_context: ADK tool execution context to save the generated image as a Playground artifact.

    Returns:
        The public HTTPS URL of the generated image stored in Cloud Storage.
    """
    import uuid
    from google import genai
    from google.genai import types
    from google.cloud import storage

    try:
        client_genai = genai.Client(vertexai=True, project="qwiklabs-gcp-03-61708ee92f67", location="global")
        res = client_genai.models.generate_content(
            model="gemini-3.1-flash-lite-image",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
            ),
        )

        image_bytes = None
        mime_type = "image/png"
        if res.candidates and res.candidates[0].content and res.candidates[0].content.parts:
            for part in res.candidates[0].content.parts:
                if part.inline_data:
                    image_bytes = part.inline_data.data
                    if part.inline_data.mime_type:
                        mime_type = part.inline_data.mime_type
                    break

        if not image_bytes:
            return "Error: Could not generate image bytes from model response."

        # 1. Save artifact for Playground Artifacts panel
        tool_context.save_artifact(
            "destination_image.png",
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
        )

        # 2. Upload directly from in-memory bytes to Cloud Storage bucket (hardcoded string)
        bucket_name = "travel-destination-explorer-media-61708"
        client_gcs = storage.Client(project="qwiklabs-gcp-03-61708ee92f67")
        bucket = client_gcs.bucket(bucket_name)
        blob_name = f"destinations/{uuid.uuid4().hex}.png"
        blob = bucket.blob(blob_name)
        blob.upload_from_string(image_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/travel-destination-explorer-media-61708/{blob_name}"
        return f"Successfully generated travel image!\nPublic URL: {public_url}"
    except Exception as e:
        return f"Error generating destination image: {str(e)}"



