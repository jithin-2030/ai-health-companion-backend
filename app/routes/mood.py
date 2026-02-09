from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

from app.database import moods_collection
from app.auth_utils import get_current_user

router = APIRouter()


class MoodRequest(BaseModel):
    """Request model for adding mood"""
    mood: str = Field(..., description="Current mood (happy, sad, anxious, angry, calm, despair, neutral)")
    intensity: int = Field(default=5, ge=1, le=10, description="Mood intensity from 1-10")
    notes: Optional[str] = Field(default=None, description="Optional notes about the mood")


class MoodResponse(BaseModel):
    """Response model for mood entry"""
    mood: str
    intensity: int
    date: str
    time: str
    notes: Optional[str] = None


class MoodHistoryResponse(BaseModel):
    """Response model for mood history"""
    total_entries: int
    moods: List[MoodResponse]
    average_intensity: float


@router.post("/mood", status_code=status.HTTP_201_CREATED)
def add_mood(
    mood_data: MoodRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Add a new mood entry for the current user.
    
    Args:
        mood_data: MoodRequest containing mood, intensity, and optional notes
        current_user: Authenticated username from JWT token
        
    Returns:
        Success message with mood entry details
    """
    try:
        mood_entry = {
            "username": current_user,
            "mood": mood_data.mood.lower(),
            "intensity": mood_data.intensity,
            "notes": mood_data.notes,
            "created_at": datetime.utcnow()
        }
        
        result = moods_collection.insert_one(mood_entry)
        
        return {
            "message": "Mood saved successfully",
            "mood_id": str(result.inserted_id),
            "mood": mood_data.mood,
            "intensity": mood_data.intensity
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving mood: {str(e)}"
        )


@router.get("/mood", response_model=MoodHistoryResponse)
def get_moods(
    current_user: str = Depends(get_current_user),
    limit: int = 100
):
    """
    Retrieve mood history for the current user.
    
    Args:
        current_user: Authenticated username from JWT token
        limit: Maximum number of mood entries to return (default: 100)
        
    Returns:
        MoodHistoryResponse with mood entries and statistics
    """
    try:
        moods = list(moods_collection.find(
            {"username": current_user},
            {"_id": 0}
        ).sort("created_at", -1).limit(limit))

        if not moods:
            return MoodHistoryResponse(
                total_entries=0,
                moods=[],
                average_intensity=0.0
            )

        result_moods = []
        total_intensity = 0

        for m in moods:
            created_at = m.get("created_at", datetime.utcnow())
            intensity = m.get("intensity", 5)
            total_intensity += intensity

            result_moods.append(MoodResponse(
                mood=m.get("mood", "unknown"),
                intensity=intensity,
                date=created_at.strftime("%Y-%m-%d"),
                time=created_at.strftime("%H:%M:%S"),
                notes=m.get("notes")
            ))

        average_intensity = total_intensity / len(moods) if moods else 0

        return MoodHistoryResponse(
            total_entries=len(moods),
            moods=result_moods,
            average_intensity=round(average_intensity, 2)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving moods: {str(e)}"
        )

