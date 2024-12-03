from dataclasses import dataclass
from typing import Optional

from core.PlayingField import PlayingField
from models.User import User


@dataclass
class Game:
    id: str
    owner: User
    playing_fields: dict[int, PlayingField]
    player: Optional[User] = None
    step_user: Optional[User] = None

    def other_user(self, user: User) -> Optional[User]:
        return self.player if user == self.owner else self.owner

    def is_user_step(self, user: User) -> bool:
        return self.step_user == user

    def next_step(self):
        self.step_user = self.player if self.step_user == self.owner else self.owner

    def playing_field(self, user: User) -> PlayingField:
        return self.playing_fields.get(user.id, None)
