
"""
models/schemas.py
-----------------
Defines simple data classes for Post, User, and Todo.
These help us work with API data as Python objects.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any



@dataclass
class Post:
    id: int
    user_id: int
    title: str
    body: str

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "Post":
        """
        Make a Post object from API data (dict).
        """
        return cls(
            id=data["id"],
            user_id=data["userId"],
            title=data["title"],
            body=data["body"],
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Convert this Post to a dict (for JSON).
        """
        return asdict(self)



@dataclass
class UserAddress:
    street: str
    suite: str
    city: str
    zipcode: str

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "UserAddress":
        """
        Make a UserAddress from API data.
        """
        return cls(
            street=data.get("street", ""),
            suite=data.get("suite", ""),
            city=data.get("city", ""),
            zipcode=data.get("zipcode", ""),
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Convert this address to a dict.
        """
        return asdict(self)



@dataclass
class User:
    id: int
    name: str
    username: str
    email: str
    phone: str
    website: str
    address: UserAddress

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "User":
        """
        Make a User object from API data.
        """
        return cls(
            id=data["id"],
            name=data["name"],
            username=data["username"],
            email=data["email"],
            phone=data.get("phone", ""),
            website=data.get("website", ""),
            address=UserAddress.from_api(data.get("address", {})),
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Convert this User to a dict.
        """
        return asdict(self)



@dataclass
class Todo:
    id: int
    user_id: int
    title: str
    completed: bool

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "Todo":
        """
        Make a Todo object from API data.
        """
        return cls(
            id=data["id"],
            user_id=data["userId"],
            title=data["title"],
            completed=data["completed"],
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Convert this Todo to a dict.
        """
        return asdict(self)
