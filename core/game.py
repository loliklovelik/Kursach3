import random
import uuid
from typing import Optional

from models.Game import Game
from core.PlayingField import PlayingField, FIELD_ROW, FIELD_COLUMN
from models.User import User

games: dict[str, Game] = dict()


async def generate_game(owner: User) -> Game:
    game_id = await generate_id()
    game = Game(id=game_id, owner=owner, playing_fields={})
    games[game_id] = game
    return game


async def generate_id() -> str:
    # return str(uuid.uuid4())
    return "1"

async def join_to_game(game_id: str, player: User) -> Optional[Game]:
    if game_id not in games:
        return None
    game = games[game_id]
    game.player = player
    game.step_user = game.owner if random.randint(0, 1) == 0 else game.player
    return game


async def end_game(game_id: str) -> None:
    games.pop(game_id, None)


async def generate_playing_field(game: Game) -> None:
    game.playing_fields[game.owner.id] = PlayingField()
    game.playing_fields[game.player.id] = PlayingField()


def check_shoot_coordinates(coordinates: str) -> bool:
    if len(coordinates) != 2 or coordinates[0].upper() not in FIELD_COLUMN or coordinates[1] not in FIELD_ROW:
        return False
    return True
