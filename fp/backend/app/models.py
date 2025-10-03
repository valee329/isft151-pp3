from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any, List

# Core data structures (match your DB columns; add fields later as needed)

@dataclass
class User:
    id: int
    name: str
    lastname: str
    id_role: Optional[int] = None
    password: Optional[str] = None  # (should be hashed later)

@dataclass
class UserProfile:
    user_id: int
    bio: Optional[str]
    location: Optional[str]
    avatar_url: Optional[str]
    created_at: Optional[datetime] = None

@dataclass
class Post:
    id: int
    user_id: int
    content: str
    created_at: datetime
    # Convenience: author display (joined fields)
    author_name: Optional[str] = None
    author_lastname: Optional[str] = None

# ---------- Mapping helpers (dict row -> model) ----------

def row_to_user(row: Dict[str, Any]) -> User:
    return User(
        id=row["id"],
        name=row["name"],
        lastname=row["lastname"],
        id_role=row.get("id_role"),
        password=row.get("password")
    )

def row_to_profile(row: Dict[str, Any]) -> UserProfile:
    return UserProfile(
        user_id=row["user_id"],
        bio=row.get("bio"),
        location=row.get("location"),
        avatar_url=row.get("avatar_url"),
        created_at=row.get("created_at")
    )

def row_to_post(row: Dict[str, Any]) -> Post:
    return Post(
        id=row["id"],
        user_id=row["user_id"],
        content=row["content"],
        created_at=row["created_at"],
        author_name=row.get("name"),
        author_lastname=row.get("lastname")
    )

def rows_to_posts(rows: List[Dict[str, Any]]) -> List[Post]:
    return [row_to_post(r) for r in rows]