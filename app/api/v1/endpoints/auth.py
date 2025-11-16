from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.user import (
    UserRegister,
    UserLogin,
    UserResponse,
    TokenResponse,
    RefreshTokenRequest
)
from app.services.auth_service import auth_service
from app.core.security import decode_token

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """
    Register a new user

    - **email**: Valid email address
    - **password**: Minimum 8 characters
    - **name**: User's full name
    """
    return await auth_service.register_user(user_data)


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """
    Login with email and password

    Returns JWT access token and refresh token
    """
    return await auth_service.login_user(credentials)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh access token using refresh token
    """
    return await auth_service.refresh_access_token(request.refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Get current authenticated user details

    Requires: Bearer token in Authorization header
    """
    token = credentials.credentials
    payload = decode_token(token)
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    return await auth_service.get_current_user(user_id)


@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Logout user (client should delete tokens)
    """
    # In JWT, logout is handled client-side by deleting tokens
    # Optional: Add token to blacklist here
    return {"message": "Successfully logged out"}
