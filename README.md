AI Mental Health Companion — Backend API

Overview

This document explains the backend API endpoints, authentication flow, and how to run the service locally. Base URL (development): http://localhost:8000

Setup

1. Copy `.env.example` to `.env` and set values (especially `GEMINI_API_KEY` and MongoDB URI).
2. Create and activate a venv, then install dependencies:

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

3. Start the server:

```powershell
uvicorn app.main:app --reload
```

Environment variables (.env)

MongoDB Atlas Setup (Recommended):
1. Go to https://www.mongodb.com/cloud/atlas
2. Create a free account and cluster
3. Get your connection string (looks like: mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority)
4. Set in .env:

- GEMINI_API_KEY=your_gemini_api_key
- MONGODB_URI=mongodb+srv://<USERNAME>:<PASSWORD>@<CLUSTER>.mongodb.net/?retryWrites=true&w=majority
- DATABASE_NAME=mental_health_db

OR for local development:
- MONGODB_URI=mongodb://localhost:27017

Authentication

- Registration: `POST /signup` — creates a user. Passwords are hashed (bcrypt).
- Login: `POST /login` — returns a Bearer JWT access token. Use this token in `Authorization: Bearer <token>` for protected endpoints.
- Protected endpoints depend on `get_current_user` which extracts the `sub` (username) from the token.

Endpoints

**POST /signup**
- Description: Register a new user.
- Request JSON:
```json
{
  "username": "jdoe",
  "email": "jdoe@example.com",
  "password": "safepassword",
  "contact": "1234567890"
}
```
- Response (201):
```json
{
  "message": "User registered successfully",
  "user_id": "<mongo_id>",
  "username": "jdoe",
  "email": "jdoe@example.com"
}
```
Notes: username and email are validated for uniqueness; password stored hashed.

**POST /login**
- Description: Authenticate with `username` and `password`.
- Request JSON:
```json
{
  "username": "jdoe",
  "password": "safepassword"
}
```
- Response (200):
```json
{
  "message": "Login successful",
  "access_token": "<jwt_token>",
  "token_type": "bearer",
  "user": {
    "username": "jdoe",
    "email": "jdoe@example.com",
    "contact": "1234567890"
  }
}
```
Use the `access_token` in the `Authorization` header for subsequent requests.

**GET /profile?username=<username>**
- Description: Retrieve a user's profile (no password returned).
- Protected: no (used for testing); consider protecting in production.

Mood endpoints

**POST /mood**
- Description: Save a mood entry for the authenticated user.
- Protected: Yes (Authorization header required).
- Request JSON:
```json
{
  "mood": "sad",
  "intensity": 7,
  "notes": "Felt low after work"
}
```
- Response (201):
```json
{
  "message": "Mood saved successfully",
  "mood_id": "<mongo_id>",
  "mood": "sad",
  "intensity": 7
}
```
Notes: stored fields include `username`, `mood`, `intensity`, `notes`, `created_at`.

**GET /mood?limit=100**
- Description: Retrieve mood history for the authenticated user. Returns total entries, mood list (date/time), and average intensity.
- Protected: Yes
- Response sample:
```json
{
  "total_entries": 12,
  "moods": [
    {"mood":"sad","intensity":7,"date":"2026-02-09","time":"14:12:03","notes":"..."},
    ...
  ],
  "average_intensity": 5.25
}
```

Recommendations

**GET /recommendations**
- Description: Returns personalized recommendations (music, movies, books, activities, exercises, meditation, food, games, resources, and tips) based on the user's latest saved mood and its intensity.
- Protected: Yes
- Response sample (partial):
```json
{
  "mood": "sad",
  "intensity": 7,
  "recommendations": {
    "music": ["Fix You - Coldplay", "Let It Be - The Beatles"],
    "movies": ["The Pursuit of Happyness", "Forrest Gump"],
    "books": ["Man's Search for Meaning - Viktor Frankl"],
    "activities": ["Talk to a trusted friend", "Journal your feelings"],
    "exercises": ["Gentle stretching (15 mins)"],
    "meditation": ["Self-compassion meditation (15 mins)"],
    "food": ["Comfort foods that nourish you"],
    "games": ["Stardew Valley"],
    "resources": ["7 Cups.io", "Crisis Text Line - text HOME to 741741"]
  },
  "tips": ["It's okay to feel sad - emotions are valid", "Reach out to someone - don't isolate"]
}
```
Notes: Includes a `despair` category with crisis resources; defaults to calm/neutral recommendations if no category match.

Chatbot

**POST /chat**
- Description: Conversational mental-health assistant powered by Gemini. Returns an empathetic reply and `emotion_analysis` (a simple emotion category produced server-side).
- Protected: Yes
- Request JSON:
```json
{
  "message": "I'm feeling really hopeless",
  "conversation_history": [
    {"role":"user","parts":["...previous message..."]},
    {"role":"model","parts":["...previous reply..."]}
  ]
}
```
- Response sample:
```json
{
  "reply": "I'm really sorry you're feeling that way...",
  "emotion_analysis": "despair"
}
```
Notes & Requirements:
- Must set `GEMINI_API_KEY` in `.env` for the chatbot to work.
- The server uses the Google Generative AI client (`google-generativeai`) to call a supported Gemini model (configured in code).
- Conversation history is optional but recommended for multi-turn context.

Error handling

- Protected endpoints return `401` for invalid or expired tokens.
- Missing mood data returns a `404` from `/recommendations` with a message to add mood first.
- Server errors return `500` with an error message.

Database

- MongoDB is used. Collections used include:
  - `users` — stores `username`, `email`, `password` (hashed), `contact`.
  - `moods` — stores mood entries linked to `username` with `intensity`, `notes`, and `created_at`.

Security notes

- Passwords are hashed with bcrypt via `passlib`.
- Use HTTPS in production and secure environment variables.
- Consider rate-limiting and stricter validation for public endpoints.

Quick curl examples

- Signup:
```bash
curl -X POST http://localhost:8000/signup -H "Content-Type: application/json" -d '{"username":"jdoe","email":"jdoe@example.com","password":"pass1234","contact":"1234567890"}'
```

- Login:
```bash
curl -X POST http://localhost:8000/login -H "Content-Type: application/json" -d '{"username":"jdoe","password":"pass1234"}'
```

- Save mood:
```bash
curl -X POST http://localhost:8000/mood -H "Authorization: Bearer <token>" -H "Content-Type: application/json" -d '{"mood":"sad","intensity":8,"notes":"Long day"}'
```

- Get recommendations:
```bash
curl -X GET http://localhost:8000/recommendations -H "Authorization: Bearer <token>"
```

Next steps

- Run `pip install -r requirements.txt` then `uvicorn app.main:app --reload` and test endpoints with the frontend or curl/Postman.
- If you want, I can also add a Postman collection or automated tests for these endpoints.
