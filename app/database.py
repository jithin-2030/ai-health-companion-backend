from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB Atlas connection via environment variable
MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb://localhost:27017"  # Fallback to local for development
)

DATABASE_NAME = os.getenv("DATABASE_NAME", "mental_health_db")

# Connect to MongoDB
client = MongoClient(MONGODB_URI)

# Create (or use) database
db = client[DATABASE_NAME]

# Create (or use) collections
users_collection = db["users"]
moods_collection = db["moods"]
