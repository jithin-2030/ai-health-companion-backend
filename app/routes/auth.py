from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from passlib.context import CryptContext
from app.database import users_collection
from app.jwt_handler import create_access_token
from typing import Optional

router = APIRouter()

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Request body structures
class SignupRequest(BaseModel):
    """Model for user registration"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    contact: str = Field(..., min_length=10)


class LoginRequest(BaseModel):
    """Model for user login"""
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)


class UserResponse(BaseModel):
    """Model for user response"""
    username: str
    email: str
    contact: str


class LoginResponse(BaseModel):
    """Model for login response"""
    message: str
    access_token: str
    token_type: str
    user: UserResponse


# Password utility functions
def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(user_data: SignupRequest):
    """
    Register a new user account.
    
    Args:
        user_data: SignupRequest containing username, email, password, and contact
        
    Returns:
        Success message with user details
    """
    try:
        # Check if username already exists
        existing_user_by_username = users_collection.find_one({"username": user_data.username})
        if existing_user_by_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )

        # Check if email already exists
        existing_user_by_email = users_collection.find_one({"email": user_data.email})
        if existing_user_by_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Hash the password
        hashed_password = hash_password(user_data.password)

        # Create user document
        user_document = {
            "username": user_data.username,
            "email": user_data.email,
            "password": hashed_password,
            "contact": user_data.contact
        }

        # Insert user into database
        result = users_collection.insert_one(user_document)

        return {
            "message": "User registered successfully",
            "user_id": str(result.inserted_id),
            "username": user_data.username,
            "email": user_data.email
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during signup: {str(e)}"
        )


@router.post("/login", response_model=LoginResponse)
def login(user_data: LoginRequest):
    """
    Authenticate user and provide access token.
    
    Args:
        user_data: LoginRequest containing username and password
        
    Returns:
        LoginResponse with access token and user information
    """
    try:
        # Find user by username
        user = users_collection.find_one({"username": user_data.username})

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )

        # Verify password
        if not verify_password(user_data.password, user["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )

        # Create access token
        token = create_access_token({"sub": user["username"]})

        return LoginResponse(
            message="Login successful",
            access_token=token,
            token_type="bearer",
            user=UserResponse(
                username=user["username"],
                email=user["email"],
                contact=user["contact"]
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during login: {str(e)}"
        )


@router.get("/profile")
def get_profile(username: str):
    """
    Get user profile information (for testing).
    
    Args:
        username: Username to fetch profile for
        
    Returns:
        User profile without password
    """
    try:
        user = users_collection.find_one({"username": username})

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return UserResponse(
            username=user["username"],
            email=user["email"],
            contact=user["contact"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching profile: {str(e)}"
        )


