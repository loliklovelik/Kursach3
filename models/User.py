from dataclasses import dataclass

import aiogram.types


@dataclass
class User:
    id: int
    username: str


def from_aiogram_user(aiogram_user: aiogram.types.User) -> User:
    return User(
        id=aiogram_user.id,
        username=aiogram_user.username,
    )
