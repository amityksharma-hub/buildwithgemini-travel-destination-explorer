# 🧪 Travel Destination Explorer — End-to-End & RAG Verification Guide

This guide provides a comprehensive step-by-step scenario to test and verify all real implemented capabilities of the **Travel Destination Explorer** agent, with special focus on validating the **Vertex AI RAG Engine (Travel Guide retrieval)**.

---

## 🌐 Application Architecture & Live URLs

* **Cloud Run Frontend Web App**: [https://travel-destination-explorer-frontend-879292600164.us-east1.run.app](https://travel-destination-explorer-frontend-879292600164.us-east1.run.app)
* **Cloud Agent Runtime (Reasoning Engine)**: `projects/879292600164/locations/us-east1/reasoningEngines/447591392458309632`
* **GitHub Repository**: [https://github.com/amityksharma-hub/buildwithgemini-travel-destination-explorer](https://github.com/amityksharma-hub/buildwithgemini-travel-destination-explorer)
* **Media Cloud Storage Bucket**: `gs://travel-destination-explorer-media-61708`

---

## 🎬 End-to-End Verification Scenario

Follow these 4 test prompts in order in the chat interface:

### 📍 Test 1: Firestore Destinations & A2UI Cards
* **User Prompt**: `Show me beach destinations`
* **Under the Hood**:
  1. The agent calls the Firestore tool `search_destinations(category="beach")`.
  2. Queries Firestore collection `destinations`.
  3. Formats results with `a2ui_utils.py` callback into A2UI schema v0.8.
* **Expected Result**: Rich interactive UI cards showing beach destinations (e.g. *Bali, Indonesia*, *Maui, USA*, *Phuket, Thailand*) with images, descriptions, tags, and ratings.

---

### ☀️ Test 2: Live Weather Tool Integration
* **User Prompt**: `What is the weather in Bali?`
* **Under the Hood**:
  1. The agent invokes `get_live_destination_weather(city_name="Bali")`.
  2. Calls the Open-Meteo Geocoding & Weather APIs.
  3. Extracts live temperature (°C), weather condition, and wind speed.
* **Expected Result**: A clear response stating the current real-time temperature and condition in Bali (e.g., *"Current weather for Bali, Indonesia: 28°C, Clear sky, Wind 12 km/h"*).

---

### 🎨 Test 3: Gemini Image Generation & GCS Upload
* **User Prompt**: `Generate an image of Santorini`
* **Under the Hood**:
  1. The agent invokes `generate_destination_image(prompt="Santorini Greece white buildings blue domes")`.
  2. Calls `imagen-3.0-generate-002` / `gemini-3.1-flash-lite-image` to generate a 1024x1024 image.
  3. Saves the image as a local artifact and uploads it to public Cloud Storage (`gs://travel-destination-explorer-media-61708/destinations/...`).
  4. Returns an A2UI card embedding the image URL.
* **Expected Result**: A stunning generated image of Santorini rendered inline inside an A2UI card.

---

### 📚 Test 4: RAG Engine — Travel Guide Document Retrieval (SPECIAL FOCUS)
* **User Prompt**: `Consult the travel guide for herbal notes`
* **Under the Hood**:
  1. The agent selects and invokes the RAG function tool `consult_travel_guide(query="herbal notes")`.
  2. Queries the Vertex AI RAG Corpus / indexed document (`pg49513.txt` - *The Herbal & Travel Guide*).
  3. Performs document chunk retrieval and returns matched passages.
  4. Grounded Gemini model reads the retrieved passages and composes a cited summary.
* **Expected Result**: Grounded passages retrieved from the travel guide document explaining herbal properties and travel lore.

---

## 🔬 Programmatic RAG Verification (Python & Curl)

You can also test the RAG Engine tool programmatically without using the web UI:

### Option A: Python Verification Script
Run the following Python snippet in your environment:

```python
from app.destination_tools import consult_travel_guide

# Test RAG retrieval query
query = "herbal notes"
retrieved_passages = consult_travel_guide(query)

print("--- RAG RETRIEVAL OUTPUT ---")
print(retrieved_passages)
```

**Expected Sample Output**:
```text
--- RAG RETRIEVAL OUTPUT ---
The Project Gutenberg eBook of The Complete Herbal
    
This eBook is for the use of anyone anywhere in the United States and
most other parts of the world...
---
_Government and virtues._ It is an herb under the dominion of Venus,
and indeed one of her darlings, though somewhat hard to come by...
```

---

### Option B: REST API Verification (Curl to Cloud Run Proxy)

Send an HTTP POST request directly to your deployed Cloud Run chat endpoint:

```bash
curl -X POST "https://travel-destination-explorer-frontend-879292600164.us-east1.run.app/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Consult the travel guide for herbal notes."}'
```

**Expected HTTP Response**:
```json
{
  "parts": [
    {
      "kind": "text",
      "text": "Based on the travel guide, here are the retrieved herbal notes:\n\n1. It is an herb under the dominion of Venus...\n2. Helps old ulcers, hot inflammations, and travel ailments."
    }
  ]
}
```

---

## ✅ Verification Checklist

| Test Item | Feature | Tool / Service | Status |
|---|---|---|---|
| **Test 1** | Beach Destinations Search | Firestore + A2UI v0.8 | ✅ Passed |
| **Test 2** | Live Weather Lookup | Open-Meteo API | ✅ Passed |
| **Test 3** | Destination Image Generation | Gemini Image Model + GCS | ✅ Passed |
| **Test 4** | Document RAG Retrieval | `consult_travel_guide` + `pg49513.txt` | ✅ Passed |
| **Test 5** | Frontend Deployment | Cloud Run + FastAPI A2A Proxy | ✅ Passed |

---
*Created for Build with Gemini 2026 Submission.*
