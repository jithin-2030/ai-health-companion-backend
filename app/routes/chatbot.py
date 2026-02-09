from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.auth_utils import get_current_user
import google.generativeai as genai
from config import SYSTEM_PROMPT, GEMINI_API_KEY
from typing import Optional, List

router = APIRouter()

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)


class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[dict]] = None


class ChatResponse(BaseModel):
    reply: str
    emotion_analysis: Optional[str] = None


@router.post("/chat", response_model=ChatResponse)
async def chat(
    chat_data: ChatRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Process chat message using Gemini API for mental health support.
    
    Args:
        chat_data: Contains the user message and optional conversation history
        current_user: Authenticated user from JWT token
        
    Returns:
        ChatResponse with AI-generated supportive response
    """
    try:
        # Initialize the Gemini model
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        # Build conversation history for context
        conversation = []
        
        # Add system context
        conversation.append({
            "role": "user",
            "parts": [SYSTEM_PROMPT]
        })
        
        conversation.append({
            "role": "model",
            "parts": ["I understand. I'm here to provide empathetic support for your mental health journey. Please feel free to share how you're feeling."]
        })
        
        # Add previous conversation history if provided
        if chat_data.conversation_history:
            for msg in chat_data.conversation_history:
                conversation.append(msg)
        
        # Add current user message
        conversation.append({
            "role": "user",
            "parts": [chat_data.message]
        })
        
        # Generate response using Gemini
        response = model.generate_content(
            contents=conversation,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                top_p=0.8,
                top_k=40,
                max_output_tokens=500,
            ),
            safety_settings=[
                {
                    "category": genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                    "threshold": genai.types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                },
                {
                    "category": genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                    "threshold": genai.types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                },
                {
                    "category": genai.types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                    "threshold": genai.types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                },
                {
                    "category": genai.types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                    "threshold": genai.types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                },
            ]
        )
        
        if not response.text:
            raise HTTPException(status_code=500, detail="Failed to generate response")
        
        # Detect emotion from user message for analytics
        emotion = detect_emotion(chat_data.message)
        
        return ChatResponse(
            reply=response.text,
            emotion_analysis=emotion
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")


def detect_emotion(message: str) -> str:
    """
    Improved emotion detection based on keywords and sentiment patterns.
    This provides analytics about the user's emotional state.
    """
    text = message.lower()
    
    # Define emotion keywords with expanded vocabulary
    emotions = {
        "despair": [
            "despair", "hopeless", "hopelessness", "no point", "no purpose", 
            "can't", "cannot", "don't care", "don't want to", "gives up",
            "worthless", "useless", "nothing matters", "fucking life", 
            "worst", "horrible", "terrible", "pathetic", "loser"
        ],
        "sad": [
            "sad", "depressed", "depression", "unhappy", "down", "miserable", 
            "melancholy", "grief", "lonely", "alone", "abandoned", "hurt",
            "heartbroken", "crying", "tears", "weeping", "empty", "numb"
        ],
        "anxious": [
            "anxious", "anxiety", "worried", "worry", "stress", "stressed",
            "nervous", "panic", "afraid", "fear", "scared", "terrified",
            "uneasy", "overwhelmed", "overwhelm", "restless", "agitation"
        ],
        "angry": [
            "angry", "anger", "mad", "furious", "rage", "frustrated", "frustrated",
            "annoyed", "irritated", "irritated", "pissed", "hate", "despise",
            "resentment", "bitter", "hostile"
        ],
        "happy": [
            "happy", "happiness", "joy", "joyful", "excited", "excitement",
            "good", "great", "wonderful", "amazing", "fantastic", "lovely",
            "blessed", "grateful", "thankful", "love"
        ],
        "calm": [
            "calm", "peaceful", "peace", "relaxed", "relax", "serene", "tranquil",
            "meditate", "meditation", "mindful", "centered", "grounded", "okay"
        ],
    }
    
    # Check for despair indicators first (highest priority)
    despair_keywords = emotions.get("despair", [])
    for word in despair_keywords:
        if word in text:
            return "despair"
    
    # Check for other emotions
    for emotion, keywords in emotions.items():
        if emotion == "despair":  # Skip despair as we already checked it
            continue
        for word in keywords:
            if word in text:
                return emotion
    
    # Pattern-based detection
    # Check for repeated negations (multiple "no" or "don't")
    negation_count = text.count(" no ") + text.count("no ") + text.count(" no") + text.count("don't") + text.count("can't")
    if negation_count >= 2:
        return "despair"
    
    # Check for combinations of negative words
    negative_words = ["bad", "worse", "worst", "fail", "failed", "waste", "dumb", "stupid", "idiot"]
    negative_count = sum(1 for word in negative_words if word in text)
    if negative_count >= 2:
        return "sad"
    
    return "neutral"

