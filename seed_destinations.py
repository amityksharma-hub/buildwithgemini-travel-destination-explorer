import subprocess
from google.cloud import firestore
from google.oauth2 import credentials

# Hardcoded project ID as required to avoid runtime project number resolution issue
PROJECT_ID = "qwiklabs-gcp-03-61708ee92f67"

def get_firestore_client():
    try:
        # Use active gcloud access token if ADC credentials fail in lab environment
        token = subprocess.check_output(["gcloud", "auth", "print-access-token"]).decode().strip()
        creds = credentials.Credentials(token)
        return firestore.Client(project=PROJECT_ID, credentials=creds)
    except Exception:
        return firestore.Client(project=PROJECT_ID)

def seed_database():
    print(f"Connecting to Firestore for project: {PROJECT_ID}")
    db = get_firestore_client()
    collection_ref = db.collection("destinations")

    sample_destinations = [
        {
            "name": "Bali",
            "country": "Indonesia",
            "description": "Tropical paradise known for iconic beaches, volcanic mountains, coral reefs, and vibrant culture.",
            "best_season": "April to October",
            "budget_level": "budget",
            "climate": "beach",
        },
        {
            "name": "Kyoto",
            "country": "Japan",
            "description": "Historic city famed for classical Buddhist temples, traditional wooden houses, shrines, and cherry blossoms.",
            "best_season": "March to May & September to November",
            "budget_level": "mid-range",
            "climate": "city",
        },
        {
            "name": "Zermatt & Swiss Alps",
            "country": "Switzerland",
            "description": "Breathtaking alpine resort famous for Matterhorn views, world-class skiing, and luxury mountain chalets.",
            "best_season": "December to March & June to August",
            "budget_level": "luxury",
            "climate": "mountain",
        },
        {
            "name": "Merzouga Desert",
            "country": "Morocco",
            "description": "Gateway to Erg Chebbi, offering vast golden sand dunes, camel safaris, and night sky stargazing in luxury camps.",
            "best_season": "October to May",
            "budget_level": "mid-range",
            "climate": "desert",
        },
        {
            "name": "Goa",
            "country": "India",
            "description": "Vibrant coastal state with golden beaches, relaxed beach shacks, night markets, and rich Portuguese heritage.",
            "best_season": "November to February",
            "budget_level": "budget",
            "climate": "beach",
        },
    ]

    for dest in sample_destinations:
        doc_id = dest["name"].lower().replace(" ", "_")
        doc_ref = collection_ref.document(doc_id)
        doc_ref.set(dest)
        print(f"Seeded destination: {dest['name']} ({dest['country']})")

    print("\nSuccessfully seeded 5 destinations into Firestore collection 'destinations'.")

if __name__ == "__main__":
    seed_database()
