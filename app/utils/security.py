from fastapi import Request
from typing import Optional
import re


def get_client_ip(request: Request) -> str:
    """Get client IP address from request, handling proxies"""
    # Check for forwarded headers (proxy/load balancer)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Take the first IP (original client)
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    
    # Fallback to direct connection
    if hasattr(request.client, "host"):
        return request.client.host
    
    return "unknown"


def get_user_agent(request: Request) -> str:
    """Get user agent string from request"""
    return request.headers.get("User-Agent", "unknown")


def sanitize_string(value: str, max_length: int = 255) -> str:
    """Sanitize string input for security"""
    if not value:
        return ""
    
    # Remove any potentially dangerous characters
    sanitized = re.sub(r'[<>"\';\\]', '', value)
    
    # Limit length
    return sanitized[:max_length]


def is_valid_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def is_strong_password(password: str) -> tuple[bool, list[str]]:
    """Check if password meets security requirements"""
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one number")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")
    
    return len(errors) == 0, errors


def parse_user_agent(user_agent: str) -> dict:
    """Parse user agent string to extract browser and OS info"""
    if not user_agent or user_agent == "unknown":
        return {"browser": "Unknown", "os": "Unknown", "device": "Unknown"}
    
    browser = "Unknown"
    os = "Unknown"
    device = "Desktop"
    
    # Browser detection
    if "Chrome" in user_agent:
        browser = "Chrome"
    elif "Firefox" in user_agent:
        browser = "Firefox"
    elif "Safari" in user_agent and "Chrome" not in user_agent:
        browser = "Safari"
    elif "Edge" in user_agent:
        browser = "Edge"
    elif "Opera" in user_agent:
        browser = "Opera"
    
    # OS detection
    if "Windows" in user_agent:
        os = "Windows"
    elif "Macintosh" in user_agent or "Mac OS X" in user_agent:
        os = "macOS"
    elif "Linux" in user_agent:
        os = "Linux"
    elif "Android" in user_agent:
        os = "Android"
        device = "Mobile"
    elif "iPhone" in user_agent or "iPad" in user_agent:
        os = "iOS"
        device = "Mobile" if "iPhone" in user_agent else "Tablet"
    
    return {
        "browser": browser,
        "os": os,
        "device": device,
        "raw": user_agent
    } 