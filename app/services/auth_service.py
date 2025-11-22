from typing import Dict, Any
from fastapi import HTTPException, status
from appwrite.exception import AppwriteException
from appwrite.id import ID
from app.core.appwrite import databases, account, get_appwrite_client
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.models.user import UserRegister, UserLogin, UserResponse, TokenResponse
from app.config import settings


class AuthService:
    @staticmethod
    async def register_user(user_data: UserRegister) -> TokenResponse:
        """Register a new user"""
        try:
            # Create Appwrite account
            user_id = ID.unique()

            # Create account in Appwrite Auth
            appwrite_user = account.create(
                user_id=user_id,
                email=user_data.email,
                password=user_data.password,
                name=user_data.name
            )

            # Create user document in database
            user_doc = databases.create_document(
                database_id=settings.APPWRITE_DATABASE_ID,
                collection_id=settings.COLLECTION_USERS,
                document_id=user_id,
                data={
                    "email": user_data.email,
                    "name": user_data.name,
                    "subscription_tier": "free",
                    "subscription_status": "active",
                    "storage_used": 0,
                    "storage_limit": 500,  # 500MB for free tier
                    "email_verified": False,
                    "created_at": appwrite_user['$createdAt'],
                }
            )

            # Generate tokens
            token_data = {"sub": user_id, "email": user_data.email}
            access_token = create_access_token(token_data)
            refresh_token = create_refresh_token(token_data)

            # Send verification email
            try:
                account.create_verification(
                    url=f"{settings.FRONTEND_URL}/verify-email")
            except:
                pass  # Don't fail registration if email fails

            user_response = UserResponse(
                id=user_id,
                email=user_doc['email'],
                name=user_doc['name'],
                subscription_tier=user_doc['subscription_tier'],
                created_at=user_doc['created_at'],
                email_verified=user_doc['email_verified']
            )

            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                user=user_response
            )

        except AppwriteException as e:
            if "user_already_exists" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User with this email already exists"
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    @staticmethod
    async def login_user(credentials: UserLogin) -> TokenResponse:
        """Login user - Updated for Appwrite 4.1.0+"""
        try:

            session = account.create_session(
                user_id=ID.unique(),
                email=credentials.email,
                password=credentials.password
            )

            user_id = session['userId']

            user_doc = databases.get_document(
                database_id=settings.APPWRITE_DATABASE_ID,
                collection_id=settings.COLLECTION_USERS,
                document_id=user_id
            )

            token_data = {"sub": user_id, "email": credentials.email}
            access_token = create_access_token(token_data)
            refresh_token = create_refresh_token(token_data)

            user_response = UserResponse(
                id=user_id,
                email=user_doc['email'],
                name=user_doc['name'],
                subscription_tier=user_doc['subscription_tier'],
                created_at=user_doc['created_at'],
                email_verified=user_doc.get('email_verified', False)
            )

            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                user=user_response
            )

        except AppwriteException as e:
            if "invalid_credentials" in str(e).lower() or "user_not_found" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Login failed"
            )

    @staticmethod
    async def get_current_user(user_id: str) -> UserResponse:
        """Get current user details"""
        try:
            user_doc = databases.get_document(
                database_id=settings.APPWRITE_DATABASE_ID,
                collection_id=settings.COLLECTION_USERS,
                document_id=user_id
            )

            return UserResponse(
                id=user_id,
                email=user_doc['email'],
                name=user_doc['name'],
                subscription_tier=user_doc['subscription_tier'],
                created_at=user_doc['created_at'],
                email_verified=user_doc.get('email_verified', False)
            )
        except AppwriteException:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

    @staticmethod
    async def refresh_access_token(refresh_token: str) -> TokenResponse:
        """Refresh access token using refresh token"""
        from app.core.security import decode_token, verify_token_type

        payload = decode_token(refresh_token)
        verify_token_type(payload, "refresh")

        user_id = payload.get("sub")
        email = payload.get("email")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        # Generate new tokens
        token_data = {"sub": user_id, "email": email}
        new_access_token = create_access_token(token_data)
        new_refresh_token = create_refresh_token(token_data)

        # Get user details
        user = await AuthService.get_current_user(user_id)

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user
        )


auth_service = AuthService()
