"""
Authentication Configuration
Defines user roles and credentials for RBAC
"""

import bcrypt
from typing import Dict, List


# User roles
class UserRole:
    ADMIN = "admin"
    DEVELOPER = "developer"
    FACULTY = "faculty"
    STUDENT = "student"


# Predefined users with hashed passwords
# Default password for all users: "mind2024" (change these in production!)
USERS = {
    "admin@mind.edu": {
        "name": "System Administrator",
        "role": UserRole.ADMIN,
        "password_hash": bcrypt.hashpw("mind2024".encode('utf-8'), bcrypt.gensalt()),
        "departments": ["All"],
        "cohorts": ["All"]
    },
    "dev@mind.edu": {
        "name": "Development Team",
        "role": UserRole.DEVELOPER,
        "password_hash": bcrypt.hashpw("mind2024".encode('utf-8'), bcrypt.gensalt()),
        "departments": ["IT"],
        "cohorts": ["All"]
    },
    "faculty@mind.edu": {
        "name": "Dr. Sarah Johnson",
        "role": UserRole.FACULTY,
        "password_hash": bcrypt.hashpw("mind2024".encode('utf-8'), bcrypt.gensalt()),
        "departments": ["Computer Science", "Engineering"],
        "cohorts": ["2024", "2025"]
    },
    "student@mind.edu": {
        "name": "John Smith",
        "role": UserRole.STUDENT,
        "password_hash": bcrypt.hashpw("mind2024".encode('utf-8'), bcrypt.gensalt()),
        "departments": ["Computer Science"],
        "cohorts": ["2025"],
        "user_id": "550e8400-e29b-41d4-a716-446655440000"  # Example UUID
    }
}


# Role permissions mapping
ROLE_PERMISSIONS = {
    UserRole.ADMIN: {
        "pages": ["Admin", "Developer", "Faculty", "Student"],
        "can_view_all_users": True,
        "can_modify_settings": True,
        "can_view_telemetry": True,
        "can_export_data": True
    },
    UserRole.DEVELOPER: {
        "pages": ["Developer"],
        "can_view_all_users": False,
        "can_modify_settings": False,
        "can_view_telemetry": True,
        "can_export_data": True
    },
    UserRole.FACULTY: {
        "pages": ["Faculty"],
        "can_view_all_users": False,
        "can_modify_settings": False,
        "can_view_telemetry": False,
        "can_export_data": True
    },
    UserRole.STUDENT: {
        "pages": ["Student"],
        "can_view_all_users": False,
        "can_modify_settings": False,
        "can_view_telemetry": False,
        "can_export_data": False
    }
}


def get_user_permissions(role: str) -> Dict:
    """Get permissions for a given role"""
    return ROLE_PERMISSIONS.get(role, {})


def can_access_page(role: str, page: str) -> bool:
    """Check if a role can access a specific page"""
    permissions = get_user_permissions(role)
    return page in permissions.get("pages", [])
