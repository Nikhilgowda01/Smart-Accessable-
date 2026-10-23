"""
Amazon One - FastAPI Application Server
Provides REST API endpoints for services, discovery, AI assistance, products, recommendations, and mock activities.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import datetime

from app.services_data import SERVICES_DATA, SERVICE_CATEGORIES

app = FastAPI(
    title="Amazon One Unified Ecosystem API",
    description="Independent hackathon prototype backend for discovery across Amazon services.",
    version="1.0.0"
)

# CORS configuration for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request / Response Schemas
class AssistantRequest(BaseModel):
    message: str
    context: Optional[dict] = None

class RecommendationRequest(BaseModel):
    interests: List[str]

class FavoriteRequest(BaseModel):
    serviceId: str


# 1. Services Endpoints
@app.get("/api/services")
def get_services(category: Optional[str] = None, q: Optional[str] = None):
    results = SERVICES_DATA
    if category and category != "All":
        results = [s for s in results if s["category"].lower() == category.lower()]
    if q:
        query = q.lower()
        results = [
            s for s in results
            if query in s["name"].lower()
            or query in s["description"].lower()
            or query in s["tagline"].lower()
            or query in s["category"].lower()
        ]
    return {
        "services": results,
        "count": len(results),
        "categories": SERVICE_CATEGORIES
    }

@app.get("/api/services/{service_id}")
def get_service_by_id(service_id: str):
    found = next((s for s in SERVICES_DATA if s["id"] == service_id), None)
    if not found:
        raise HTTPException(status_code=404, detail=f"Service with id '{service_id}' was not found.")
    return found


# 2. AI Service Discovery Assistant Endpoint
@app.post("/api/assistant")
def ask_assistant(req: AssistantRequest):
    query = req.message.lower().strip()
    reply = ""
    matched_services = []

    # Natural language discovery logic
    if any(k in query for k in ["grocer", "vegetable", "fruit", "food", "milk", "fresh"]):
        matched_services = [s for s in SERVICES_DATA if s["id"] == "amazon-fresh"]
        reply = "For ordering groceries, fresh organic produce, and pantry staples with same-day 2-hour delivery, Amazon Fresh is your dedicated service."

    elif any(k in query for k in ["audiobook", "listen to book", "narrat", "audible", "podcast"]):
        matched_services = [s for s in SERVICES_DATA if s["id"] in ["audible", "amazon-music"]]
        reply = "For audiobooks, bestselling narration, and exclusive spoken-word audio, Audible is Amazon's flagship platform. For podcasts and streaming songs, you can also explore Amazon Music."

    elif any(k in query for k in ["song", "music", "kannada", "hindi", "playlist", "album", "artist"]):
        matched_services = [s for s in SERVICES_DATA if s["id"] == "amazon-music"]
        reply = "Amazon Music provides over 100 million songs in lossless Ultra HD and spatial audio, with curated regional Indian playlists including Kannada, Hindi, and global hits."

    elif any(k in query for k in ["host", "website", "cloud", "server", "compute", "ec2", "s3", "storage", "devops"]):
        matched_services = [s for s in SERVICES_DATA if s["id"] == "aws"]
        reply = "For hosting websites, managing virtual compute instances (EC2), and object storage (S3), Amazon Web Services (AWS) is the world's most comprehensive cloud infrastructure."

    elif any(k in query for k in ["publish", "author", "write", "paperback", "royalt", "kdp"]):
        matched_services = [s for s in SERVICES_DATA if s["id"] == "kdp"]
        reply = "You can self-publish digital e-books and physical print-on-demand paperbacks for free using Kindle Direct Publishing (KDP), earning up to 70% royalties globally."

    elif any(k in query for k in ["smart", "device", "echo", "alexa", "home", "light", "speaker"]):
        matched_services = [s for s in SERVICES_DATA if s["id"] in ["alexa-echo", "fire-tv"]]
        reply = "Alexa & Echo devices allow you to control smart-home lights, thermostats, and routines hands-free using conversational voice commands."

    elif any(k in query for k in ["pay", "wallet", "checkout", "card", "transaction", "upi"]):
        matched_services = [s for s in SERVICES_DATA if s["id"] == "amazon-pay"]
        reply = "Amazon Pay provides safe, 1-click checkout across partner merchants online using your stored Amazon billing methods and A-to-z buyer guarantees."

    elif any(k in query for k in ["movie", "show", "series", "video", "cinema", "prime video"]):
        matched_services = [s for s in SERVICES_DATA if s["id"] == "prime-video"]
        reply = "Prime Video offers award-winning original shows, 4K blockbuster movies, and live sports included with your Prime membership."

    else:
        # Generic match based on keywords
        scored = []
        for s in SERVICES_DATA:
            score = 0
            for word in query.split():
                if len(word) > 2 and word in (s["name"] + " " + s["description"] + " " + s["tagline"]).lower():
                    score += 1
            if score > 0:
                scored.append((score, s))
        scored.sort(key=lambda x: x[0], reverse=True)

        if scored:
            matched_services = [item[1] for item in scored[:2]]
            reply = f"Based on your inquiry, {matched_services[0]['name']} is a strong fit. Here is how it can assist your goal:"
        else:
            matched_services = [s for s in SERVICES_DATA if s["isFeatured"]][:3]
            reply = "I am your Amazon One AI concierge. I can guide you to the exact service across Shopping, Payments, Cloud, Smart Devices, or Entertainment for any task. Try asking: 'Where can I listen to audiobooks?' or 'Which service hosts websites?'"

    return {
        "reply": reply,
        "matchedServices": matched_services,
        "timestamp": datetime.datetime.now().strftime("%I:%M %p"),
        "source": "Amazon One AI Engine",
        "suggestedQueries": [
            "Which Amazon service can help me buy groceries?",
            "Where can I listen to audiobooks?",
            "Which service is useful for hosting my website?",
            "How can I publish my own book?",
            "Which Amazon service can help me manage smart-home devices?"
        ]
    }


# 3. Personalized Recommendations
@app.post("/api/recommendations")
def get_recommendations(req: RecommendationRequest):
    user_interests = [i.lower() for i in req.interests]
    recommended = []

    for service in SERVICES_DATA:
        # Check category match
        if service["category"].lower() in user_interests:
            recommended.append(service)

    # Fallback to featured
    if not recommended:
        recommended = [s for s in SERVICES_DATA if s["isFeatured"]]

    return {
        "recommendations": recommended,
        "selectedInterests": req.interests
    }


# 4. Dashboard Summary Metrics
@app.get("/api/dashboard")
def get_dashboard_summary():
    return {
        "appName": "Amazon One",
        "totalServices": len(SERVICES_DATA),
        "categoriesCount": len(SERVICE_CATEGORIES) - 1,
        "activeServices": 7,
        "simulatedSavings": "$124.50",
        "mockRecentActivity": [
            {"service": "Prime Video", "action": "Watched Fallout S1:E4", "time": "2 hours ago"},
            {"service": "Amazon Shopping", "action": "Order #403-912 Delivered", "time": "Yesterday"},
            {"service": "Kindle", "action": "Read 24 pages of Atomic Habits", "time": "2 days ago"},
            {"service": "Amazon Music", "action": "Streamed Discovery Weekly", "time": "3 days ago"}
        ]
    }


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "Amazon One Backend", "version": "1.0.0"}
