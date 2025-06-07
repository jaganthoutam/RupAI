#!/usr/bin/env python3
"""
Initialize demo users for testing the authentication system.
This script creates admin, operator, and viewer users with known credentials.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.config.settings import settings
from app.auth.models import User
from app.db.database import Base


def create_demo_users():
    """Create demo users for testing"""
    
    # Create engine and session
    engine = create_engine(settings.DATABASE_URL.replace('+asyncpg', ''))
    Session = sessionmaker(bind=engine)
    
    # Create tables if they don't exist
    Base.metadata.create_all(engine)
    
    session = Session()
    
    try:
        # Demo users data
        demo_users = [
            {
                "email": "admin@payment.com",
                "name": "System Administrator",
                "password": "admin123456",
                "role": "admin",
                "permissions": [
                    "payments.create",
                    "payments.read",
                    "payments.update",
                    "payments.delete",
                    "wallets.create",
                    "wallets.read",
                    "wallets.update",
                    "wallets.delete",
                    "users.create",
                    "users.read",
                    "users.update",
                    "users.delete",
                    "audit.read",
                    "settings.update",
                    "system.monitor"
                ]
            },
            {
                "email": "operator@payment.com",
                "name": "Payment Operator",
                "password": "operator123",
                "role": "operator",
                "permissions": [
                    "payments.create",
                    "payments.read",
                    "payments.update",
                    "wallets.create",
                    "wallets.read",
                    "wallets.update",
                    "audit.read"
                ]
            },
            {
                "email": "viewer@payment.com",
                "name": "System Viewer",
                "password": "viewer123",
                "role": "viewer",
                "permissions": [
                    "payments.read",
                    "wallets.read",
                    "audit.read"
                ]
            }
        ]
        
        created_users = []
        
        for user_data in demo_users:
            # Check if user already exists
            existing_user = session.query(User).filter(User.email == user_data["email"]).first()
            
            if existing_user:
                print(f"👤 User {user_data['email']} already exists - updating...")
                existing_user.name = user_data["name"]
                existing_user.role = user_data["role"]
                existing_user.permissions = user_data["permissions"]
                existing_user.set_password(user_data["password"])
                existing_user.is_active = True
                existing_user.is_verified = True
                created_users.append(existing_user)
            else:
                print(f"✨ Creating user {user_data['email']}...")
                user = User(
                    email=user_data["email"],
                    name=user_data["name"],
                    role=user_data["role"],
                    permissions=user_data["permissions"],
                    is_active=True,
                    is_verified=True
                )
                user.set_password(user_data["password"])
                session.add(user)
                created_users.append(user)
        
        # Commit the changes
        session.commit()
        
        print(f"\n🎉 Successfully created/updated {len(created_users)} demo users!")
        print("\n📋 Demo Credentials:")
        print("=" * 50)
        
        for user in created_users:
            password = next(u["password"] for u in demo_users if u["email"] == user.email)
            print(f"👤 {user.role.upper()}")
            print(f"   Email: {user.email}")
            print(f"   Password: {password}")
            print(f"   Role: {user.role}")
            print(f"   Permissions: {len(user.permissions or [])} permissions")
            print()
        
        print("🔐 You can now use these credentials to log into the admin panel!")
        
    except Exception as e:
        print(f"❌ Error creating demo users: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    print("🚀 Initializing demo users...")
    create_demo_users()
    print("✅ Demo users initialization complete!") 