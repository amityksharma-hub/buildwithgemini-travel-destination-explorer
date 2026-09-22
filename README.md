# Travel Destination Explorer 🌴

An agentic AI travel assistant built with the **Google Agent Development Kit (ADK)** and deployed to **Google Cloud Agent Runtime**. Features personalized recommendations, durable user preferences, live weather metrics, RAG document retrieval, AI image generation, sandboxed code execution, and A2UI rich visual cards.

![Travel Destination Explorer Demo](./demo.gif)

---

## 🛠 Implemented Features

### 🧠 Vertex AI Memory Bank
* **Durable Cross-Session Memory**: Automatically extracts and retains user travel preferences (budget, climate, travel style, solo/family status) across separate conversation sessions using Vertex AI Memory Bank.
* **Preload Memory**: Uses `PreloadMemoryTool` and `generate_memories_callback` to personalize recommendations dynamically based on past interactions.

### 🗄 Firestore Destination Database & User Favorites
* **Destination Catalog**: Queries and manages curated travel destinations in Google Cloud Firestore.
* **Tools**:
  * `search_destinations(budget, climate, country)`: Searches destinations by budget level (`budget`, `moderate`, `luxury`), climate (`tropical`, `temperate`, `cold`), or country.
  * `add_destination(name, country, climate, budget, description, highlights)`: Adds new destination spots to the database.
  * `save_favorite_destination(user_id, destination_name)`: Saves user favorite destinations with timestamps in Firestore.
  * `get_favorite_destinations(user_id)`: Retrieves the user's saved favorites list.

### 🌤 Live Open-Meteo Weather Integration
* **Real-Time Weather Metrics**: Converts queried city names into geographic coordinates using Open-Meteo Geocoding API and fetches live weather data.
* **Tool**: `get_live_destination_weather(query)`: Returns current temperature (°C / °F), weather conditions (e.g. clear sky, rain, fog), and wind speed.

### 📚 Vertex AI RAG Engine Document Retrieval
* **Vector Search Grounding**: Grounded on Project Gutenberg travel literature (`pg49513.txt`) indexed inside a serverless Vertex AI RAG Engine corpus (`us-west1`).
* **Tool**: `consult_travel_guide(query)`: Queries the document corpus to provide historical travel facts, plant/herbal descriptions, and local lore.

### 🎨 Destination Image Generation & Cloud Storage
* **Imagen / Flash Lite Generation**: Generates travel destination artwork on demand using `gemini-3.1-flash-lite-image` in the `global` region.
* **Tool**: `generate_destination_image(prompt)`: Saves generated image artifacts to the Playground panel AND uploads raw image bytes directly from memory to Google Cloud Storage (`travel-destination-explorer-media-61708`), returning a public HTTPS image URL.

### 🧮 Agent Platform Code Execution Sandbox
* **Secure Python Sandbox**: Runs Python code inside `AgentEngineSandboxCodeExecutor` for exact travel calculations.
* **Calculations**: Calculates trip cost estimates, currency conversions, daily budget splits, and date/day count math securely.

### 🖼 A2UI Rich Visual Cards
* **Structured UI Rendering**: Implements `A2uiSchemaManager` (version `0.8`) with the Basic Catalog and `a2ui_callback` model callback.
* **Rich Layouts**: Renders response payloads as structured A2UI cards (`Card`, `Column`, `Row`, `Text`, `Image`, `Icon`) instead of plain unformatted text.

### 🚀 FastAPI Proxy & Cloud Run Frontend
* **A2A Protocol Proxy**: A lightweight FastAPI proxy (`frontend/main.py`) that authenticates browser requests via Application Default Credentials and communicates with Agent Runtime over the Agent-to-Agent (A2A) protocol.
* **Rebranded Interface**: Features a Tropical Teal responsive chat UI (`frontend/static/index.html`) with quick-action prompt chips for instant destination exploration.

---

## 📁 Repository Structure

```
.
├── README.md                   # Project documentation & feature overview
├── demo.gif                    # Animated walkthrough demo GIF
├── agents-cli-manifest.yaml    # Agent Runtime deployment specification
├── pyproject.toml              # Python package configuration and dependencies
├── app/
│   ├── agent.py                # Root ADK agent configuration & A2UI callback setup
│   ├── destination_tools.py    # Firestore, Weather, RAG, and Image Generation tools
│   └── a2ui_utils.py           # A2UI response rewrapping and surface sanitizer
└── frontend/
    ├── main.py                 # FastAPI proxy handling browser -> A2A agent routing
    ├── Procfile                # Cloud Run buildpack entrypoint
    ├── requirements.txt        # Frontend proxy dependencies
    └── static/
        └── index.html          # Chat interface with A2UI card renderer
```

---

## ⚙️ Deployment Specification

* **Framework**: Google Agent Development Kit (ADK)
* **Agent Engine Deployment**: Google Cloud Agent Runtime (`us-east1`)
* **Frontend Service**: Google Cloud Run (`us-east1`)
* **Service Account Security**: Configured with `roles/aiplatform.user`, `roles/datastore.user`, and `roles/storage.objectAdmin`.
