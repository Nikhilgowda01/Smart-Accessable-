
"""
Amazon One - FastAPI Application Server

Provides REST API endpoints for services, discovery, AI assistance,
recommendations, dashboard metrics, and AccessAble smart-home control.
"""

import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.services_data import SERVICES_DATA, SERVICE_CATEGORIES
from app.smart_home import router as smart_home_router


app = FastAPI(
    title="Amazon One Unified Ecosystem API",
    description=(
        "Hackathon backend for Amazon service discovery "
        "and the AccessAble accessible smart-home assistant."
    ),
    version="1.0.0",
)

app.include_router(smart_home_router)


# CORS configuration for the React frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




# Request schemas
class AssistantRequest(BaseModel):
    message: str
    context: Optional[dict] = None


class RecommendationRequest(BaseModel):
    interests: List[str]


class FavoriteRequest(BaseModel):
    serviceId: str


# 1. Services endpoints
@app.get("/api/services")
def get_services(
    category: Optional[str] = None,
    q: Optional[str] = None,
):
    results = SERVICES_DATA

    if category and category != "All":
        results = [
            service
            for service in results
            if service["category"].lower() == category.lower()
        ]

    if q:
        query = q.lower()
        results = [
            service
            for service in results
            if query in service["name"].lower()
            or query in service["description"].lower()
            or query in service["tagline"].lower()
            or query in service["category"].lower()
        ]

    return {
        "services": results,
        "count": len(results),
        "categories": SERVICE_CATEGORIES,
    }


@app.get("/api/services/{service_id}")
def get_service_by_id(service_id: str):
    found = next(
        (service for service in SERVICES_DATA if service["id"] == service_id),
        None,
    )

    if not found:
        raise HTTPException(
            status_code=404,
            detail=f"Service with id '{service_id}' was not found.",
        )

    return found


# 2. AI service discovery assistant endpoint
# Keep this endpoint compatible with the existing frontend.
@app.post("/api/assistant")
def ask_assistant(req: AssistantRequest):
    query = req.message.lower().strip()
    reply = ""
    matched_services = []

    if any(
        word in query
        for word in ["grocer", "vegetable", "fruit", "food", "milk", "fresh"]
    ):
        matched_services = [
            service
            for service in SERVICES_DATA
            if service["id"] == "amazon-fresh"
        ]
        reply = (
            "For ordering groceries, fresh organic produce, and pantry "
            "staples, Amazon Fresh is your dedicated service."
        )

    elif any(
        word in query
        for word in ["audiobook", "listen to book", "narrat", "audible", "podcast"]
    ):
        matched_services = [
            service
            for service in SERVICES_DATA
            if service["id"] in ["audible", "amazon-music"]
        ]
        reply = (
            "For audiobooks and spoken-word audio, explore Audible. "
            "For podcasts and streaming music, explore Amazon Music."
        )

    elif any(
        word in query
        for word in ["song", "music", "kannada", "hindi", "playlist", "album", "artist"]
    ):
        matched_services = [
            service
            for service in SERVICES_DATA
            if service["id"] == "amazon-music"
        ]
        reply = (
            "Amazon Music offers music streaming and regional playlists, "
            "including Kannada and Hindi music."
        )

    elif any(
        word in query
        for word in ["host", "website", "cloud", "server", "compute", "ec2", "s3", "storage", "devops"]
    ):
        matched_services = [
            service for service in SERVICES_DATA if service["id"] == "aws"
        ]
        reply = (
            "Amazon Web Services provides cloud infrastructure, "
            "compute services, and storage."
        )

    elif any(
        word in query
        for word in ["publish", "author", "write", "paperback", "royalt", "kdp"]
    ):
        matched_services = [
            service for service in SERVICES_DATA if service["id"] == "kdp"
        ]
        reply = (
            "Kindle Direct Publishing lets authors publish e-books "
            "and eligible print books."
        )

    elif any(
        word in query
        for word in ["smart", "device", "echo", "alexa", "home", "light", "speaker"]
    ):
        matched_services = [
            service
            for service in SERVICES_DATA
            if service["id"] in ["alexa-echo", "fire-tv"]
        ]
        reply = (
            "Alexa and Echo devices support conversational control "
            "of compatible smart-home devices."
        )

    elif any(
        word in query
        for word in ["pay", "wallet", "checkout", "card", "transaction", "upi"]
    ):
        matched_services = [
            service for service in SERVICES_DATA if service["id"] == "amazon-pay"
        ]
        reply = (
            "Amazon Pay supports payment and checkout experiences "
            "across supported services and merchants."
        )

    elif any(
        word in query
        for word in ["movie", "show", "series", "video", "cinema", "prime video"]
    ):
        matched_services = [
            service
            for service in SERVICES_DATA
            if service["id"] == "prime-video"
        ]
        reply = "Explore Prime Video for movies, shows, and other video content."

    else:
        # Generic keyword-based service matching.
        scored = []

        for service in SERVICES_DATA:
            searchable_text = (
                service["name"]
                + " "
                + service["description"]
                + " "
                + service["tagline"]
            ).lower()

            score = sum(
                1
                for word in query.split()
                if len(word) > 2 and word in searchable_text
            )

            if score > 0:
                scored.append((score, service))

        scored.sort(key=lambda item: item[0], reverse=True)

        if scored:
            matched_services = [item[1] for item in scored[:2]]
            reply = (
                f"Based on your inquiry, {matched_services[0]['name']} "
                "may be a good fit for your needs."
            )
        else:
            matched_services = [
                service
                for service in SERVICES_DATA
                if service["isFeatured"]
            ][:3]

            reply = (
                "I am your Amazon One service assistant. Ask me about "
                "Shopping, Payments, Cloud, Smart Devices, or Entertainment."
            )

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
            "Which Amazon service can help me manage smart-home devices?",
        ],
    }


# 3. Personalized recommendations
@app.post("/api/recommendations")
def get_recommendations(req: RecommendationRequest):
    user_interests = [interest.lower() for interest in req.interests]
    recommended = []

    for service in SERVICES_DATA:
        if service["category"].lower() in user_interests:
            recommended.append(service)

    if not recommended:
        recommended = [
            service for service in SERVICES_DATA if service["isFeatured"]
        ]

    return {
        "recommendations": recommended,
        "selectedInterests": req.interests,
    }


# 4. Dashboard summary metrics
@app.get("/api/dashboard")
def get_dashboard_summary():
    return {
        "appName": "Amazon One",
        "totalServices": len(SERVICES_DATA),
        "categoriesCount": len(SERVICE_CATEGORIES) - 1,
        "activeServices": 7,
        "simulatedSavings": "$124.50",
        "mockRecentActivity": [
            {
                "service": "Prime Video",
                "action": "Watched Fallout S1:E4",
                "time": "2 hours ago",
            },
            {
                "service": "Amazon Shopping",
                "action": "Order #403-912 Delivered",
                "time": "Yesterday",
            },
            {
                "service": "Kindle",
                "action": "Read 24 pages of Atomic Habits",
                "time": "2 days ago",
            },
            {
                "service": "Amazon Music",
                "action": "Streamed Discovery Weekly",
                "time": "3 days ago",
            },
        ],
    }


# 5. Health check
@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "service": "Amazon One Backend",
        "version": "1.0.0",
    }
