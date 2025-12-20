from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime
from typing import Optional, Dict, Any

from app.core.database import get_db
from app.core.config import settings
from app.schemas import User, SubscriptionTier
from app.services.user import UserService

security = HTTPBearer()

def verify_clerk_token(token: str) -> dict:
    """
    Verifies a Clerk-issued JWT token.
    Returns a dictionary containing user data from the token.
    """
    # Local testing mode fallback
    if settings.TESTING_MODE and token == "dev-secret-key-for-testing-only":
        return {
            "auth_provider_id": "dev_user_123",
            "email": "dev@example.com",
            "first_name": "Dev",
            "last_name": "User"
        }

    if not all([settings.CLERK_PEM_PUBLIC_KEY, settings.CLERK_JWT_ISSUER, settings.CLERK_JWT_AUDIENCE]):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Clerk authentication not fully configured. Please set CLERK_PEM_PUBLIC_KEY, CLERK_JWT_ISSUER, and CLERK_JWT_AUDIENCE environment variables."
        )

    try:
        # Clerk uses RS256 algorithm and requires verification with its public key.
        # The issuer (iss) and audience (azp) claims are also validated.
        payload = jwt.decode(
            token,
            key=settings.CLERK_PEM_PUBLIC_KEY,
            algorithms=["RS256"],
            audience=settings.CLERK_JWT_AUDIENCE,
            issuer=settings.CLERK_JWT_ISSUER,
            options={"verify_signature": True, "verify_aud": True, "verify_iss": True}
        )
        
        # Extract user information
        # 'sub' is the user ID in Clerk's JWT
        # 'email_addresses' is an array, take the first one if available
        email = None
        if payload.get("email_addresses") and len(payload["email_addresses"]) > 0:
            email = payload["email_addresses"][0].get("email_address")

        user_data = {
            "auth_provider_id": payload.get("sub"),
            "email": email,
            "first_name": payload.get("given_name"),
            "last_name": payload.get("family_name")
        }
        
        return user_data
    except JWTError as e:
        print(f"JWT Verification Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        print(f"Unexpected Auth Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unexpected authentication error",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        user_data = verify_clerk_token(credentials.credentials)
        user_service = UserService(db)
        user = user_service.get_user_by_auth_id(user_data["auth_provider_id"])

        if user is None:
            if settings.TESTING_MODE:
                # In testing mode, automatically create the user if they don't exist
                user = user_service.get_or_create_user(user_data)
            else:
                raise credentials_exception

        return user
    except HTTPException:
        # Re-raise any HTTPExceptions from verify_clerk_token or our own logic
        raise
    except (JWTError, Exception):
        raise credentials_exception

def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    if not credentials:
        return None
        
    try:
        user_data = verify_clerk_token(credentials.credentials)
        user_service = UserService(db)
        return user_service.get_user_by_auth_id(user_data["auth_provider_id"])
    except JWTError:
        return None