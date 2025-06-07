"""
User Management API Endpoints
Provides comprehensive user CRUD operations, role management, and authentication.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import uuid4, UUID
import hashlib

from fastapi import APIRouter, HTTPException, Depends, Query, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.user import User, UserRole
from ..services.auth_service import AuthService
from ..db.session import get_db
from ..auth.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["User Management"])
security = HTTPBearer()

# Request/Response Models
class UserCreateRequest(BaseModel):
    """User creation request model."""
    email: EmailStr = Field(..., description="User email address")
    name: str = Field(..., min_length=2, max_length=100, description="User full name")
    password: str = Field(..., min_length=8, description="User password")
    role: UserRole = Field(default=UserRole.USER, description="User role")
    permissions: List[str] = Field(default=[], description="Additional permissions")

class UserUpdateRequest(BaseModel):
    """User update request model."""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    role: Optional[UserRole] = None
    permissions: Optional[List[str]] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    """User response model."""
    id: str
    email: str
    name: str
    role: UserRole
    permissions: List[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    profile_picture: Optional[str] = None
    total_transactions: int = 0
    total_spent: float = 0.0

class UserListResponse(BaseModel):
    """User list response model."""
    users: List[UserResponse]
    total: int
    page: int
    limit: int
    has_next: bool
    has_prev: bool

class UserStatsResponse(BaseModel):
    """User statistics response model."""
    total_users: int
    active_users: int
    inactive_users: int
    admin_users: int
    operator_users: int
    regular_users: int
    new_users_today: int
    new_users_this_week: int
    new_users_this_month: int

# Mock user data for demonstration
MOCK_USERS = [
    {
        "id": str(uuid4()),
        "email": "admin@payment.com",
        "name": "System Administrator",
        "role": UserRole.ADMIN,
        "permissions": ["*"],
        "is_active": True,
        "created_at": datetime.now() - timedelta(days=365),
        "updated_at": datetime.now(),
        "last_login": datetime.now() - timedelta(hours=2),
        "total_transactions": 1250,
        "total_spent": 125000.0
    },
    {
        "id": str(uuid4()),
        "email": "operator@payment.com", 
        "name": "Payment Operator",
        "role": UserRole.OPERATOR,
        "permissions": ["payments.read", "payments.write", "wallets.read"],
        "is_active": True,
        "created_at": datetime.now() - timedelta(days=180),
        "updated_at": datetime.now(),
        "last_login": datetime.now() - timedelta(hours=1),
        "total_transactions": 850,
        "total_spent": 67500.0
    },
    {
        "id": str(uuid4()),
        "email": "analyst@payment.com",
        "name": "Data Analyst", 
        "role": UserRole.ANALYST,
        "permissions": ["analytics.read", "reports.read"],
        "is_active": True,
        "created_at": datetime.now() - timedelta(days=90),
        "updated_at": datetime.now(),
        "last_login": datetime.now() - timedelta(minutes=30),
        "total_transactions": 450,
        "total_spent": 32100.0
    },
    {
        "id": str(uuid4()),
        "email": "user@payment.com",
        "name": "Regular User",
        "role": UserRole.USER,
        "permissions": ["profile.read"],
        "is_active": True,
        "created_at": datetime.now() - timedelta(days=30),
        "updated_at": datetime.now(),
        "last_login": datetime.now() - timedelta(minutes=15),
        "total_transactions": 25,
        "total_spent": 1250.0
    }
]

# Add more mock users for realistic data
for i in range(5, 101):
    MOCK_USERS.append({
        "id": str(uuid4()),
        "email": f"user_{i:03d}@example.com",
        "name": f"User {i:03d}",
        "role": UserRole.USER if i % 4 != 0 else (UserRole.OPERATOR if i % 8 == 0 else UserRole.ANALYST),
        "permissions": ["profile.read"] + (["payments.read"] if i % 3 == 0 else []),
        "is_active": i % 10 != 0,  # 10% inactive users
        "created_at": datetime.now() - timedelta(days=i),
        "updated_at": datetime.now() - timedelta(days=i//2),
        "last_login": datetime.now() - timedelta(hours=i % 72) if i % 5 != 0 else None,
        "total_transactions": max(0, 100 - i + (i % 50)),
        "total_spent": max(0.0, (100 - i + (i % 50)) * 45.67)
    })

@router.get("/", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    role: Optional[UserRole] = Query(None, description="Filter by role"),
    active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search by name or email"),
    current_user: Dict = Depends(get_current_user)
):
    """Get paginated list of users with filters."""
    try:
        # Apply filters
        filtered_users = MOCK_USERS.copy()
        
        if role:
            filtered_users = [u for u in filtered_users if u["role"] == role]
        
        if active is not None:
            filtered_users = [u for u in filtered_users if u["is_active"] == active]
        
        if search:
            search_lower = search.lower()
            filtered_users = [
                u for u in filtered_users 
                if search_lower in u["name"].lower() or search_lower in u["email"].lower()
            ]
        
        total = len(filtered_users)
        start = (page - 1) * limit
        end = start + limit
        page_users = filtered_users[start:end]
        
        # Convert to response format
        user_responses = [
            UserResponse(
                id=user["id"],
                email=user["email"],
                name=user["name"],
                role=user["role"],
                permissions=user["permissions"],
                is_active=user["is_active"],
                created_at=user["created_at"],
                updated_at=user["updated_at"],
                last_login=user.get("last_login"),
                total_transactions=user.get("total_transactions", 0),
                total_spent=user.get("total_spent", 0.0)
            )
            for user in page_users
        ]
        
        return UserListResponse(
            users=user_responses,
            total=total,
            page=page,
            limit=limit,
            has_next=end < total,
            has_prev=page > 1
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch users: {str(e)}"
        )

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreateRequest,
    current_user: Dict = Depends(get_current_user)
):
    """Create a new user."""
    try:
        # Check if email already exists
        existing_user = next((u for u in MOCK_USERS if u["email"] == user_data.email), None)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        new_user = {
            "id": str(uuid4()),
            "email": user_data.email,
            "name": user_data.name,
            "role": user_data.role,
            "permissions": user_data.permissions,
            "is_active": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "last_login": None,
            "total_transactions": 0,
            "total_spent": 0.0
        }
        
        MOCK_USERS.append(new_user)
        
        return UserResponse(**new_user)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Get user by ID."""
    try:
        user = next((u for u in MOCK_USERS if u["id"] == user_id), None)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse(**user)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user: {str(e)}"
        )

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdateRequest,
    current_user: Dict = Depends(get_current_user)
):
    """Update user by ID."""
    try:
        user_index = next((i for i, u in enumerate(MOCK_USERS) if u["id"] == user_id), None)
        if user_index is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user = MOCK_USERS[user_index]
        
        # Update fields
        if user_data.name is not None:
            user["name"] = user_data.name
        if user_data.role is not None:
            user["role"] = user_data.role
        if user_data.permissions is not None:
            user["permissions"] = user_data.permissions
        if user_data.is_active is not None:
            user["is_active"] = user_data.is_active
        
        user["updated_at"] = datetime.now()
        
        return UserResponse(**user)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )

@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Delete user by ID."""
    try:
        user_index = next((i for i, u in enumerate(MOCK_USERS) if u["id"] == user_id), None)
        if user_index is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Remove user
        deleted_user = MOCK_USERS.pop(user_index)
        
        return {"message": f"User {deleted_user['email']} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )

@router.get("/stats/overview", response_model=UserStatsResponse)
async def get_user_stats(
    current_user: Dict = Depends(get_current_user)
):
    """Get user statistics overview."""
    try:
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=7)
        month_start = today_start - timedelta(days=30)
        
        total_users = len(MOCK_USERS)
        active_users = len([u for u in MOCK_USERS if u["is_active"]])
        inactive_users = total_users - active_users
        
        admin_users = len([u for u in MOCK_USERS if u["role"] == UserRole.ADMIN])
        operator_users = len([u for u in MOCK_USERS if u["role"] == UserRole.OPERATOR])
        regular_users = len([u for u in MOCK_USERS if u["role"] == UserRole.USER])
        
        new_users_today = len([u for u in MOCK_USERS if u["created_at"] >= today_start])
        new_users_this_week = len([u for u in MOCK_USERS if u["created_at"] >= week_start])
        new_users_this_month = len([u for u in MOCK_USERS if u["created_at"] >= month_start])
        
        return UserStatsResponse(
            total_users=total_users,
            active_users=active_users,
            inactive_users=inactive_users,
            admin_users=admin_users,
            operator_users=operator_users,
            regular_users=regular_users,
            new_users_today=new_users_today,
            new_users_this_week=new_users_this_week,
            new_users_this_month=new_users_this_month
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user stats: {str(e)}"
        )

@router.post("/{user_id}/activate")
async def activate_user(
    user_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Activate a user account."""
    try:
        user_index = next((i for i, u in enumerate(MOCK_USERS) if u["id"] == user_id), None)
        if user_index is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        MOCK_USERS[user_index]["is_active"] = True
        MOCK_USERS[user_index]["updated_at"] = datetime.now()
        
        return {"message": "User activated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to activate user: {str(e)}"
        )

@router.post("/{user_id}/deactivate")
async def deactivate_user(
    user_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Deactivate a user account."""
    try:
        user_index = next((i for i, u in enumerate(MOCK_USERS) if u["id"] == user_id), None)
        if user_index is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        MOCK_USERS[user_index]["is_active"] = False
        MOCK_USERS[user_index]["updated_at"] = datetime.now()
        
        return {"message": "User deactivated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deactivate user: {str(e)}"
        )

@router.get("/{user_id}/permissions")
async def get_user_permissions(
    user_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Get user permissions."""
    try:
        user = next((u for u in MOCK_USERS if u["id"] == user_id), None)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "user_id": user_id,
            "role": user["role"],
            "permissions": user["permissions"],
            "effective_permissions": user["permissions"] + (["*"] if user["role"] == UserRole.ADMIN else [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user permissions: {str(e)}"
        )

@router.put("/{user_id}/permissions")
async def update_user_permissions(
    user_id: str,
    permissions: List[str],
    current_user: Dict = Depends(get_current_user)
):
    """Update user permissions."""
    try:
        user_index = next((i for i, u in enumerate(MOCK_USERS) if u["id"] == user_id), None)
        if user_index is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        MOCK_USERS[user_index]["permissions"] = permissions
        MOCK_USERS[user_index]["updated_at"] = datetime.now()
        
        return {"message": "User permissions updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user permissions: {str(e)}"
        ) 