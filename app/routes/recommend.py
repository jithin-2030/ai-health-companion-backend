from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Dict, List, Optional
from app.auth_utils import get_current_user
from app.database import moods_collection

router = APIRouter()


class Recommendations(BaseModel):
    """Model for recommendations"""
    music: List[str]
    movies: List[str]
    books: List[str]
    activities: List[str]
    exercises: List[str]
    meditation: List[str]
    food: List[str]
    games: List[str]
    resources: List[str]


class RecommendationResponse(BaseModel):
    """Response model for recommendations"""
    mood: str
    intensity: Optional[int] = None
    recommendations: Recommendations
    tips: List[str]


# Comprehensive recommendation database
RECOMMENDATIONS_DB = {
    "happy": {
        "music": [
            "Happy - Pharrell Williams",
            "Good Life - OneRepublic",
            "Walking on Sunshine - Katrina & The Waves",
            "Don't Stop Me Now - Queen",
            "Shut Up and Dance - Walk the Moon",
            "I Gotta Feeling - The Black Eyed Peas"
        ],
        "movies": [
            "The Intern",
            "Paddington",
            "Forrest Gump",
            "The Grand Budapest Hotel",
            "Amelie",
            "Breakfast at Tiffany's",
            "Clueless",
            "Legally Blonde"
        ],
        "books": [
            "The Alchemist - Paulo Coelho",
            "Atomic Habits - James Clear",
            "Smile - Raina Telgemeier",
            "The House in the Cerulean Sea - TJ Klune",
            "Educated - Tara Westover"
        ],
        "activities": [
            "Go for a nature walk",
            "Call a friend or family member",
            "Try a new hobby or craft",
            "Dance to your favorite songs",
            "Visit a local park or beach",
            "Have a picnic with friends",
            "Try a new restaurant",
            "Volunteer for a cause you care about"
        ],
        "exercises": [
            "Dance workout (30 mins)",
            "Light jog or walk (20-30 mins)",
            "Basketball or sports with friends",
            "Yoga flow (beginner-friendly)",
            "Swimming",
            "Cycling around your area"
        ],
        "meditation": [
            "Gratitude meditation (10 mins) - focus on things you're grateful for",
            "Loving-kindness meditation (15 mins) - spread positivity",
            "Visualization of future goals (10 mins)",
            "Mindful walking meditation (20 mins)"
        ],
        "food": [
            "Your favorite comfort foods",
            "Fresh fruits and smoothies",
            "Celebrate with desserts you love",
            "Try a new recipe or cuisine",
            "Have a coffee or tea with a friend"
        ],
        "games": [
            "Among Us with friends",
            "Stardew Valley",
            "Minecraft",
            "Mario Kart",
            "Animal Crossing",
            "Board games with family"
        ],
        "resources": [
            "Positive Psychology Podcast",
            "TED Talks on Happiness",
            "Your Favorite Music Playlist"
        ],
        "tips": [
            "Share your happiness with others - it spreads joy!",
            "Capture this moment through photos or journaling",
            "Plan something fun to look forward to",
            "Express gratitude to someone today"
        ]
    },
    "sad": {
        "music": [
            "Fix You - Coldplay",
            "Let It Be - The Beatles",
            "Someone Like You - Adele",
            "The Night We Met - Lord Huron",
            "Skinny Love - Bon Iver",
            "Tears in Heaven - Eric Clapton",
            "Mad World - Gary Jules"
        ],
        "movies": [
            "The Pursuit of Happyness",
            "Forrest Gump",
            "Life is Beautiful",
            "About Time",
            "The Shawshank Redemption",
            "Good Will Hunting",
            "Silver Linings Playbook"
        ],
        "books": [
            "Man's Search for Meaning - Viktor Frankl",
            "The Comfort Book - Matt Haig",
            "It's Kind of a Funny Story - Ned Vizzini",
            "The Midnight Library - Matt Haig",
            "Educated - Tara Westover",
            "The Boy Who Harnessed the Wind - William Kamkwamba"
        ],
        "activities": [
            "Talk to a trusted friend or family member",
            "Spend time in nature",
            "Journal your feelings",
            "Visit someone you care about",
            "Engage in a favorite hobby",
            "Volunteer to help others (gives purpose)",
            "Create something - art, music, writing"
        ],
        "exercises": [
            "Gentle stretching (15 mins)",
            "Slow walk in nature (30 mins)",
            "Yoga for depression (30 mins)",
            "Swimming (therapeutic)",
            "Pilates (low-intensity)",
            "Indoor cycling (moderate pace)"
        ],
        "meditation": [
            "Self-compassion meditation (15 mins) - be kind to yourself",
            "Grounding meditation (10 mins) - bring focus to the present",
            "Body scan meditation (20 mins) - release tension",
            "Breathing exercises (5-10 mins) - calm the nervous system"
        ],
        "food": [
            "Comfort foods that nourish you",
            "Herbal tea (chamomile, lavender)",
            "Dark chocolate (rich in mood-boosting compounds)",
            "Foods rich in omega-3: salmon, nuts, seeds",
            "Warm soup or stew",
            "Vitamin-rich fruits and vegetables"
        ],
        "games": [
            "Stardew Valley (peaceful & therapeutic)",
            "Journey (artistic & emotional)",
            "Spiritfarer (bittersweet & meaningful)",
            "Abzu (calm & meditative)",
            "Cozy Grove"
        ],
        "resources": [
            "7 Cups.io (free emotional support)",
            "Trevor Project (if struggling with identity)",
            "NAMI.org (mental health resources)",
            "Crisis Text Line - text HOME to 741741"
        ],
        "tips": [
            "It's okay to feel sad - emotions are valid",
            "Reach out to someone - don't isolate",
            "Do one small positive action today",
            "Remember this feeling is temporary and will pass",
            "Consider speaking with a mental health professional"
        ]
    },
    "anxious": {
        "music": [
            "Weightless - Marconi Union",
            "Lo-fi Study Beats (YouTube)",
            "Classical Music for Anxiety",
            "Calm - Leann Rimes",
            "Breathe - Pink Floyd",
            "The Sound of Silence - Simon & Garfunkel"
        ],
        "movies": [
            "Julie & Julia",
            "Little Miss Sunshine",
            "Amelie",
            "The Secret Life of Walter Mitty",
            "Garden State",
            "Moonrise Kingdom"
        ],
        "books": [
            "The Power of Now - Eckhart Tolle",
            "Feeling Good - David D. Burns",
            "Anxious - Joseph LeDoux",
            "The Anxiety and Phobia Workbook - Edmund J. Bourne",
            "Hope and Help for Your Nerves - Claire Weekes"
        ],
        "activities": [
            "Progressive muscle relaxation",
            "Spend time in a quiet space",
            "Aromatherapy with essential oils",
            "Chew gum or eat slowly",
            "Call a supportive friend",
            "Organize or clean your space",
            "Engage in creative activities"
        ],
        "exercises": [
            "Slow yoga sequences (Yin or Restorative Yoga)",
            "Walking meditation (20 mins)",
            "Progressive muscle relaxation (15 mins)",
            "Tai Chi",
            "Low-impact aerobics",
            "Stretching routines"
        ],
        "meditation": [
            "4-7-8 breathing technique (calms nervous system)",
            "Body scan meditation (20 mins) - release worry",
            "Guided anxiety relief meditation (10-15 mins)",
            "Box breathing (4-4-4-4 pattern)",
            "Mindfulness meditation (focus on present moment)"
        ],
        "food": [
            "Chamomile or passionflower tea",
            "Dark chocolate (small amounts)",
            "Complex carbs: whole grains, oats",
            "Magnesium-rich foods: spinach, almonds, dark chocolate",
            "Probiotics: yogurt, kombucha",
            "Avoid caffeine for now"
        ],
        "games": [
            "Flow Free",
            "Monument Valley",
            "Alto's Adventure",
            "Rooms: The Unsolvable Puzzle",
            "Unpacking"
        ],
        "resources": [
            "Headspace (meditation & mindfulness)",
            "Calm App (sleep & anxiety relief)",
            "ADAA.org (Anxiety & Depression Association)",
            "Therapy for anxiety - consider professional support"
        ],
        "tips": [
            "Grounding technique: Focus on 5 things you see, 4 you touch, 3 you hear, 2 you smell, 1 you taste",
            "Remember: Anxiety is a feeling that will pass",
            "Avoid excessive news or social media",
            "Practice deep breathing regularly",
            "Set boundaries with stressful situations"
        ]
    },
    "angry": {
        "music": [
            "Lose Yourself - Eminem",
            "Believer - Imagine Dragons",
            "Seven Nation Army - The White Stripes",
            "Bulls on Parade - Rage Against the Machine",
            "Sad But True - Metallica",
            "Smells Like Teen Spirit - Nirvana"
        ],
        "movies": [
            "Rocky",
            "The Dark Knight",
            "Gladiator",
            "V for Vendetta",
            "Crouching Tiger, Hidden Dragon",
            "Fight Club"
        ],
        "books": [
            "Emotional Intelligence - Daniel Goleman",
            "Can't Hurt Me - David Goggins",
            "The Anger Solution - Ned Hallowell",
            "Why Buddhism is True - Robert Wright",
            "Atomic Habits - James Clear (channel anger into habits)"
        ],
        "activities": [
            "High-intensity workout (release tension)",
            "Hit a punching bag or pillow",
            "Go for a run or sprint",
            "Scream into a pillow",
            "Break up cardboard or ice",
            "Cold water shower",
            "Intense cleaning or organizing"
        ],
        "exercises": [
            "Kickboxing or punch combinations (30-45 mins)",
            "High-intensity interval training (HIIT)",
            "Running or sprinting (30 mins)",
            "Weightlifting (heavy weights)",
            "Jump rope (10-15 mins)",
            "Mountain climbing or plyometrics"
        ],
        "meditation": [
            "Loving-kindness meditation (15 mins) - transform anger to compassion",
            "Fire breathing (2 mins) - forceful exhales to release",
            "Walking meditation (fast-paced) (20 mins)",
            "Tonglen meditation - breathe in pain, exhale compassion"
        ],
        "food": [
            "Spicy foods (jalapenos, curry, hot sauce)",
            "Red fruits: pomegranate, watermelon, berries",
            "Protein-rich foods: chicken, fish, lean beef",
            "Complex carbs: brown rice, sweet potato",
            "Herbal teas to cool down: chamomile, passionflower"
        ],
        "games": [
            "God of War",
            "Devil May Cry",
            "Beat Saber (VR)",
            "Just Cause series",
            "Angry Birds (symbolic)"
        ],
        "resources": [
            "Anger Management Classes",
            "Cognitive Behavioral Therapy (CBT) for anger",
            "NAMI.org resources",
            "Warmline.org (peer support)"
        ],
        "tips": [
            "Take a timeout before responding",
            "Use 'I' statements: 'I feel angry because...'",
            "Channel anger into productive activity",
            "Practice assertiveness, not aggression",
            "Identify triggers and plan responses"
        ]
    },
    "calm": {
        "music": [
            "River - Leon Bridges",
            "Classical Focus - various composers",
            "Sunset - The Midnight",
            "Dreams - The Cranberries",
            "Hang - Seokyoung",
            "Clair de Lune - Claude Debussy"
        ],
        "movies": [
            "Before Sunrise",
            "About Time",
            "Fantastic Mr. Fox",
            "Isle of Dogs",
            "Arrival",
            "Her",
            "The Secret Garden"
        ],
        "books": [
            "Ikigai - Hector Garcia",
            "Deep Work - Cal Newport",
            "The Midnight Library - Matt Haig",
            "Atomic Habits - James Clear",
            "The Little Prince - Antoine de Saint-Exupery"
        ],
        "activities": [
            "Meditation or mindfulness practice",
            "Journaling your thoughts",
            "Reading a book",
            "Sketching or drawing",
            "Listening to ambient sounds (rain, ocean)",
            "Gardening or plant care",
            "Brewing tea mindfully"
        ],
        "exercises": [
            "Hatha Yoga (slow and meditative) (30-45 mins)",
            "Tai Chi (flowing, graceful movements) (30 mins)",
            "Gentle stretching (20 mins)",
            "Walking meditation (30 mins)",
            "Pilates for flexibility (25 mins)",
            "Swimming (slow, relaxing pace) (30 mins)"
        ],
        "meditation": [
            "Loving-kindness meditation (20 mins) - nurture compassion",
            "Body scan (30 mins) - awareness and relaxation",
            "Visualization meditation (15 mins) - peaceful place",
            "Mantra meditation (10 mins) - repeat calming words"
        ],
        "food": [
            "Herbal teas: chamomile, lavender, passionflower",
            "Warm porridge or oatmeal",
            "Fresh fruit and honey",
            "Nuts and seeds (balanced nutrition)",
            "Cooking and eating mindfully",
            "Avoid stimulants: caffeine, sugar"
        ],
        "games": [
            "Stardew Valley",
            "Journey",
            "Abzu",
            "Unpacking",
            "A Short Hike",
            "Animal Crossing"
        ],
        "resources": [
            "Insight Timer (free meditation app)",
            "10% Happier (meditation app)",
            "Yoga with Adriene (YouTube)",
            "Stoicism resources for calm mindset"
        ],
        "tips": [
            "Maintain this state by continuing regular meditation",
            "Create a calm environment: soft lighting, plants",
            "Protect your peace - set boundaries",
            "Practice gratitude daily",
            "Share calm with others through kindness"
        ]
    },
    "despair": {
        "music": [
            "Alive - Pearl Jam",
            "Hurt - Nine Inch Nails (or Johnny Cash version)",
            "Breathe - Pink Floyd",
            "Better Days - Goo Goo Dolls",
            "Don't Give Up - Peter Gabriel & Kate Bush"
        ],
        "movies": [
            "The Shawshank Redemption",
            "Life is Beautiful",
            "Good Will Hunting",
            "Silver Linings Playbook",
            "The Pursuit of Happyness"
        ],
        "books": [
            "Man's Search for Meaning - Viktor Frankl (ESSENTIAL)",
            "The Midnight Library - Matt Haig",
            "Courage to Change (AA/NA literature)",
            "My Lobotomy - Howard Dully (hopeful transformation)",
            "Permission to Feel - Marc Brackett"
        ],
        "activities": [
            "REACH OUT TO SOMEONE - don't isolate",
            "Crisis hotline (call or text)",
            "Contact a mental health professional immediately",
            "Visit a trusted person",
            "Take a cold shower to reset",
            "Step outside for fresh air",
            "Write a letter expressing your feelings"
        ],
        "exercises": [
            "Walk outside in daylight (20-30 mins)",
            "Any movement - just start with 5 mins",
            "Swimming (therapeutic and calming)",
            "Dance therapy",
            "Outdoor hike in nature"
        ],
        "meditation": [
            "Crisis breathing: slow, deliberate deep breaths",
            "Grounding meditation (10 mins) - anchor to present",
            "Self-compassion meditation (15 mins) - you deserve kindness",
            "Guided meditation for suicidal thoughts"
        ],
        "food": [
            "Eat something nourishing - your body matters",
            "Drink water - hydration affects mood",
            "Comfort foods that provide care for yourself",
            "Consider alcohol and drug avoidance"
        ],
        "games": [
            "Celeste (about hope and perseverance)",
            "Gris (emotional artistic journey)",
            "Spiritfarer (finding meaning in relationships)",
            "Outer Wilds (cosmic perspective)"
        ],
        "resources": [
            "NATIONAL SUICIDE PREVENTION HOTLINE: 988 (US)",
            "Crisis Text Line: Text HOME to 741741",
            "International Association for Suicide Prevention: https://www.iasp.info/resources/Crisis_Centres/",
            "NAMI Helpline: 1-800-950-NAMI (6264)",
            "SAMHSA National Helpline: 1-800-662-4357",
            "Trevor Project (LGBTQ+): 1-866-488-7386",
            "Psychology Today therapist finder"
        ],
        "tips": [
            "YOU ARE NOT ALONE - many have felt this way and recovered",
            "This feeling is temporary - seek professional help NOW",
            "Your life has value and meaning, even if you cannot see it",
            "Call someone today - a friend, family, or crisis hotline",
            "Write down reasons to stay - you'll remember later",
            "Remove means of self-harm if possible",
            "Create a safety plan with a mental health professional"
        ]
    }
}


@router.get("/recommendations", response_model=RecommendationResponse)
def get_recommendations(current_user: str = Depends(get_current_user)):
    """
    Get personalized recommendations based on the user's latest mood.
    
    Args:
        current_user: Authenticated username from JWT token
        
    Returns:
        RecommendationResponse with tailored recommendations
    """
    try:
        # Get latest mood
        latest_mood = moods_collection.find_one(
            {"username": current_user},
            sort=[("created_at", -1)]
        )

        if not latest_mood:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No mood data found. Please add a mood first."
            )

        mood = latest_mood.get("mood", "neutral").lower()
        intensity = latest_mood.get("intensity", 5)

        # Get recommendations or use neutral as fallback
        mood_recommendations = RECOMMENDATIONS_DB.get(mood)
        
        if not mood_recommendations:
            mood_recommendations = RECOMMENDATIONS_DB.get("calm")  # Default to calm
            mood = "neutral"

        return RecommendationResponse(
            mood=mood,
            intensity=intensity,
            recommendations=Recommendations(
                music=mood_recommendations.get("music", []),
                movies=mood_recommendations.get("movies", []),
                books=mood_recommendations.get("books", []),
                activities=mood_recommendations.get("activities", []),
                exercises=mood_recommendations.get("exercises", []),
                meditation=mood_recommendations.get("meditation", []),
                food=mood_recommendations.get("food", []),
                games=mood_recommendations.get("games", []),
                resources=mood_recommendations.get("resources", [])
            ),
            tips=mood_recommendations.get("tips", [])
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving recommendations: {str(e)}"
        )
