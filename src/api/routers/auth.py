from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from ... import services, security, database
from ...schemas import user as user_schema
from ...hashing import verify_password
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/register",
    response_model=user_schema.UserPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email and password"
)
def register_user(
    user: user_schema.UserCreate, 
    db: Session = Depends(database.get_db)
):
    """Register a new user"""
    try:
        db_user = services.user_service.get_user_by_email(db, email=user.email)
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Email already registered"
            )
        return services.user_service.create_user(db=db, user=user)
    except OperationalError as e:
        logger.error(f"Database connection error during registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection unavailable. Please check your internet connection or try again later."
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during registration"
        )


@router.post(
    "/login", 
    response_model=user_schema.TokenWithRefresh,
    summary="Login to get access token",
    description="Authenticate with email and password to receive JWT tokens"
)
def login_for_access_token(
    db: Session = Depends(database.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """Login and get access and refresh tokens"""
    try:
        user = services.user_service.get_user_by_email(db, email=form_data.username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )

        services.user_service.update_user_last_login(db, user.customer_id)
        
        token_data = {"sub": str(user.customer_id), "role": user.role}
        access_token = security.create_access_token(data=token_data)
        refresh_token = security.create_refresh_token(data=token_data)
        
        return {
            "access_token": access_token, 
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    except OperationalError as e:
        logger.error(f"Database connection error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection unavailable. Please check your internet connection or try again later."
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during login"
        )


@router.post(
    "/refresh",
    response_model=user_schema.Token,
    summary="Refresh access token",
    description="Get a new access token using a refresh token"
)
def refresh_access_token(
    refresh_request: user_schema.RefreshTokenRequest,
    db: Session = Depends(database.get_db)
):
    """Refresh access token using refresh token"""
    try:
        payload = security.verify_token(refresh_request.refresh_token, token_type="refresh")
        customer_id = payload.get("sub")
        role = payload.get("role")
        
        if not customer_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Verify user still exists and is active
        user = services.user_service.get_user_by_id(db, customer_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new access token
        access_token = security.create_access_token(
            data={"sub": customer_id, "role": role}
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.get(
    "/me", 
    response_model=user_schema.UserPublic,
    summary="Get current user",
    description="Get the currently authenticated user's information"
)
def read_users_me(
    current_user: user_schema.UserPublic = Depends(security.get_current_user),
):
    """Get current user information"""
    return current_user