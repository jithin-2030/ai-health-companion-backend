from app.routes import auth
from app.database import users_collection
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth_utils import get_current_user
from fastapi import Depends

from app.routes import mood

from app.routes import recommend

from app.routes import chatbot





app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router)
app.include_router(mood.router)
app.include_router(recommend.router)
app.include_router(chatbot.router)





@app.get("/")
def root():
    return {"message": "Backend is running successfully"}

@app.get("/health")
def health():
    return {"status": "healthy"}
@app.get("/test-db")
def test_db():
    users_collection.insert_one({"test": "MongoDB connected"})
    return {"message": "MongoDB connection successful"}

@app.get("/protected")
def protected_route(current_user: str = Depends(get_current_user)):
    return {
        "message": "You are authorized",
        "user": current_user
    }
