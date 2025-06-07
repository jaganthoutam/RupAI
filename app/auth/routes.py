from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from app.db.session import get_db
from app.auth.models import User, LoginAttempt
from app.auth.jwt_service import jwt_service
from app.utils.security import get_client_ip, get_user_agent

logger = logging.getLogger(__name__)
security = HTTPBearer()

router = APIRouter(prefix="/auth", tags=["Authentication"])


# Pydantic models for request/response
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int = 1800  # 30 minutes
    user: Dict[str, Any]


class RefreshRequest(BaseModel):
    refresh_token: str


class RefreshResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int = 1800


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: str
    permissions: list
    is_active: bool
    last_login: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class CreateUserRequest(BaseModel):
    email: EmailStr
    name: str
    password: str
    role: str = "viewer"
    permissions: list = []


class RegisterRequest(BaseModel):
    email: EmailStr
    name: str
    password: str
    phone: Optional[str] = None


async def log_login_attempt(
    email: str, 
    success: bool, 
    ip_address: str, 
    user_agent: str, 
    failure_reason: str = None,
    db: AsyncSession = None
):
    """Log login attempt for security monitoring"""
    try:
        login_attempt = LoginAttempt(
            email=email,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            failure_reason=failure_reason
        )
        db.add(login_attempt)
        await db.commit()
        
        logger.info(f"Login attempt: {email} - {'Success' if success else 'Failed'} from {ip_address}")
    except Exception as e:
        logger.error(f"Failed to log login attempt: {e}")


@router.post("/login", response_model=LoginResponse)
async def login(
    request: Request,
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Admin login endpoint"""
    ip_address = get_client_ip(request)
    user_agent = get_user_agent(request)
    
    try:
        # Find user by email
        result = await db.execute(select(User).filter(User.email == login_data.email))
        user = result.scalar_one_or_none()
        
        if not user:
            await log_login_attempt(
                login_data.email, False, ip_address, user_agent, 
                "User not found", db
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Check if account is locked
        if user.is_account_locked():
            await log_login_attempt(
                login_data.email, False, ip_address, user_agent, 
                "Account locked", db
            )
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Account is temporarily locked due to multiple failed login attempts"
            )
        
        # Check if user is active
        if not user.is_active:
            await log_login_attempt(
                login_data.email, False, ip_address, user_agent, 
                "Account inactive", db
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is inactive"
            )
        
        # Verify password
        if not user.check_password(login_data.password):
            user.increment_login_attempts()
            await db.commit()
            
            await log_login_attempt(
                login_data.email, False, ip_address, user_agent, 
                "Invalid password", db
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Successful login
        user.reset_login_attempts()
        await db.commit()
        
        # Create tokens
        access_token = jwt_service.create_access_token(user)
        refresh_token = await jwt_service.create_refresh_token(
            user, db, user_agent, ip_address
        )
        
        await log_login_attempt(
            login_data.email, True, ip_address, user_agent, None, db
        )
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=user.to_dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        await log_login_attempt(
            login_data.email, False, ip_address, user_agent, 
            "System error", db
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed due to system error"
        )


@router.post("/register", response_model=LoginResponse)
async def register(
    request: Request,
    register_data: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """Public customer registration endpoint"""
    ip_address = get_client_ip(request)
    user_agent = get_user_agent(request)
    
    try:
        # Check if user already exists
        result = await db.execute(select(User).filter(User.email == register_data.email))
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create new user
        new_user = User(
            email=register_data.email,
            name=register_data.name,
            role="user",  # Default role for customers
            permissions=[],  # Default permissions
            is_active=True,
            is_verified=True  # Auto-verify for demo purposes
        )
        new_user.set_password(register_data.password)
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        # Create tokens for immediate login
        access_token = jwt_service.create_access_token(new_user)
        refresh_token = await jwt_service.create_refresh_token(
            new_user, db, user_agent, ip_address
        )
        
        await log_login_attempt(
            register_data.email, True, ip_address, user_agent, None, db
        )
        
        logger.info(f"New user registered: {new_user.email}")
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=new_user.to_dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed due to system error"
        )


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_token(
    refresh_data: RefreshRequest,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token"""
    try:
        access_token, new_refresh_token = await jwt_service.refresh_access_token(
            refresh_data.refresh_token, db
        )
        
        return RefreshResponse(
            access_token=access_token,
            refresh_token=new_refresh_token
        )
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise


@router.post("/logout")
async def logout(
    refresh_data: RefreshRequest,
    db: AsyncSession = Depends(get_db)
):
    """Logout and revoke refresh token"""
    await jwt_service.revoke_refresh_token(refresh_data.refresh_token, db)
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Get current user info"""
    payload = jwt_service.verify_access_token(credentials.credentials)
    
    result = await db.execute(select(User).filter(User.id == payload["sub"]))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(**user.to_dict())


@router.put("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Change user password"""
    payload = jwt_service.verify_access_token(credentials.credentials)
    
    result = await db.execute(select(User).filter(User.id == payload["sub"]))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify current password
    if not user.check_password(password_data.current_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Set new password
    user.set_password(password_data.new_password)
    await db.commit()
    
    # Revoke all existing refresh tokens for security
    await jwt_service.revoke_all_user_tokens(str(user.id), db)
    
    return {"message": "Password changed successfully"}


# Admin-only routes
@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: CreateUserRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Create new user (admin only)"""
    payload = jwt_service.verify_access_token(credentials.credentials)
    
    # Check if current user is admin
    result = await db.execute(select(User).filter(User.id == payload["sub"]))
    current_user = result.scalar_one_or_none()
    if not current_user or current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Check if user already exists
    result = await db.execute(select(User).filter(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Create new user
    new_user = User(
        email=user_data.email,
        name=user_data.name,
        role=user_data.role,
        permissions=user_data.permissions,
        is_active=True,
        is_verified=True
    )
    new_user.set_password(user_data.password)
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    logger.info(f"Admin {current_user.email} created user {new_user.email}")
    
    return UserResponse(**new_user.to_dict())


@router.get("/users")
async def list_users(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """List all users (admin only)"""
    payload = jwt_service.verify_access_token(credentials.credentials)
    
    # Check if current user is admin
    result = await db.execute(select(User).filter(User.id == payload["sub"]))
    current_user = result.scalar_one_or_none()
    if not current_user or current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    result = await db.execute(select(User).offset(skip).limit(limit))
    users = result.scalars().all()
    return [UserResponse(**user.to_dict()) for user in users]


@router.get("/login-attempts")
async def get_login_attempts(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """Get login attempts (admin only)"""
    payload = jwt_service.verify_access_token(credentials.credentials)
    
    # Check if current user is admin
    result = await db.execute(select(User).filter(User.id == payload["sub"]))
    current_user = result.scalar_one_or_none()
    if not current_user or current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    result = await db.execute(select(LoginAttempt).order_by(
        LoginAttempt.attempted_at.desc()
    ).offset(skip).limit(limit))
    attempts = result.scalars().all()
    
    return [
        {
            "id": str(attempt.id),
            "email": attempt.email,
            "ip_address": attempt.ip_address,
            "success": attempt.success,
            "failure_reason": attempt.failure_reason,
            "attempted_at": attempt.attempted_at.isoformat()
        }
        for attempt in attempts
    ]


@router.get("/token-stats")
async def get_token_stats(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Get token statistics (admin only)"""
    payload = jwt_service.verify_access_token(credentials.credentials)
    
    # Check if current user is admin
    result = await db.execute(select(User).filter(User.id == payload["sub"]))
    current_user = result.scalar_one_or_none()
    if not current_user or current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    stats = await jwt_service.get_token_stats(db)
    return stats 