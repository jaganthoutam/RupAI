import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.auth.models import User, RefreshToken
from app.config.settings import settings


class JWTService:
    """JWT Authentication Service"""
    
    def __init__(self):
        self.secret_key = settings.JWT_SECRET_KEY
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 30

    def create_access_token(self, user: User) -> str:
        """Create JWT access token"""
        now = datetime.utcnow()
        expire = now + timedelta(minutes=self.access_token_expire_minutes)
        
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "permissions": user.permissions or [],
            "iat": now,
            "exp": expire,
            "type": "access"
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    async def create_refresh_token(self, user: User, db: AsyncSession, device_info: str = None, ip_address: str = None) -> str:
        """Create refresh token and store in database"""
        # Generate secure random token
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        # Create refresh token record
        refresh_token = RefreshToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=datetime.utcnow() + timedelta(days=self.refresh_token_expire_days),
            device_info=device_info,
            ip_address=ip_address
        )
        
        db.add(refresh_token)
        await db.commit()
        
        return token

    def verify_access_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode access token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            if payload.get("type") != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

    async def verify_refresh_token(self, token: str, db: AsyncSession) -> Optional[RefreshToken]:
        """Verify refresh token"""
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        result = await db.execute(select(RefreshToken).filter(
            RefreshToken.token_hash == token_hash
        ))
        refresh_token = result.scalar_one_or_none()
        
        if not refresh_token or not refresh_token.is_valid():
            return None
        
        return refresh_token

    async def refresh_access_token(self, refresh_token: str, db: AsyncSession) -> Tuple[str, str]:
        """Generate new access token using refresh token"""
        refresh_token_obj = await self.verify_refresh_token(refresh_token, db)
        
        if not refresh_token_obj:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
        
        # Get user
        result = await db.execute(select(User).filter(User.id == refresh_token_obj.user_id))
        user = result.scalar_one_or_none()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new access token
        new_access_token = self.create_access_token(user)
        
        # Optionally create new refresh token (token rotation)
        new_refresh_token = await self.create_refresh_token(
            user, db, 
            refresh_token_obj.device_info,
            refresh_token_obj.ip_address
        )
        
        # Revoke old refresh token
        refresh_token_obj.revoke()
        await db.commit()
        
        return new_access_token, new_refresh_token

    async def revoke_refresh_token(self, token: str, db: AsyncSession) -> bool:
        """Revoke refresh token"""
        refresh_token_obj = await self.verify_refresh_token(token, db)
        
        if refresh_token_obj:
            refresh_token_obj.revoke()
            await db.commit()
            return True
        
        return False

    async def revoke_all_user_tokens(self, user_id: str, db: AsyncSession) -> None:
        """Revoke all refresh tokens for a user"""
        result = await db.execute(select(RefreshToken).filter(
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked == False
        ))
        tokens = result.scalars().all()
        
        for token in tokens:
            token.revoke()
        
        await db.commit()

    async def clean_expired_tokens(self, db: AsyncSession) -> int:
        """Clean up expired refresh tokens"""
        result = await db.execute(select(RefreshToken).filter(
            RefreshToken.expires_at < datetime.utcnow()
        ))
        expired_tokens = result.scalars().all()
        
        count = len(expired_tokens)
        for token in expired_tokens:
            await db.delete(token)
        
        await db.commit()
        return count

    async def get_token_stats(self, db: AsyncSession) -> Dict[str, int]:
        """Get token statistics"""
        # Total tokens
        result = await db.execute(select(RefreshToken))
        total_tokens = len(result.scalars().all())
        
        # Active tokens
        result = await db.execute(select(RefreshToken).filter(
            RefreshToken.is_revoked == False,
            RefreshToken.expires_at > datetime.utcnow()
        ))
        active_tokens = len(result.scalars().all())
        
        # Expired tokens
        result = await db.execute(select(RefreshToken).filter(
            RefreshToken.expires_at < datetime.utcnow()
        ))
        expired_tokens = len(result.scalars().all())
        
        # Revoked tokens
        result = await db.execute(select(RefreshToken).filter(
            RefreshToken.is_revoked == True
        ))
        revoked_tokens = len(result.scalars().all())
        
        return {
            "total": total_tokens,
            "active": active_tokens,
            "expired": expired_tokens,
            "revoked": revoked_tokens
        }


# Global JWT service instance
jwt_service = JWTService() 