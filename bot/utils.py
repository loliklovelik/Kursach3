from typing import Optional

from aiogram import Bot
from aiogram.client.default import Default
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.fsm.storage.base import BaseStorage, StorageKey
from aiogram.types import ReplyKeyboardMarkup

from bot.SessionStep import STATE_KEY_GAME
from core.PlayingField import STRIKE_WATER_SYMBOL, WATER_SYMBOL, SHIP_SYMBOL, STRIKE_SHIP_SYMBOL
from models.Game import Game
from models.ShootType import ShootType
from models.User import User


async def set_state_to_user(
        bot: Bot,
        storage: BaseStorage,
        user: User,
        state: State,
        new_data: Optional[dict] = None,
) -> None:
    user_id = user.id
    user_key = StorageKey(bot.id, user_id, user_id)
    context = FSMContext(storage=storage, key=user_key)
    await context.set_state(state)
    if new_data is not None:
        await context.set_data(new_data)


async def send_message_to_user(
        bot: Bot,
        user: User,
        message: str,
        reply_markup: Optional[ReplyKeyboardMarkup] = None,
        parse_mode: Optional[ParseMode] = Default("parse_mode"),
) -> None:
    if reply_markup is not None:
        await bot.send_message(user.id, message, reply_markup=reply_markup, parse_mode=parse_mode)
    else:
        await bot.send_message(user.id, message, parse_mode=parse_mode)


async def send_message_and_set_state_to_user(
        bot: Bot,
        storage: BaseStorage,
        user: Optional[User],
        message: str,
        state: State,
        new_data: Optional[dict] = None,
        reply_markup: Optional[ReplyKeyboardMarkup] = None,
) -> None:
    if user is None:
        return
    await set_state_to_user(
        bot=bot,
        storage=storage,
        user=user,
        state=state,
        new_data=new_data,
    )
    await send_message_to_user(
        bot=bot,
        user=user,
        message=message,
        reply_markup=reply_markup,
    )


async def get_game_from_state(state: FSMContext) -> Optional[Game]:
    data = await state.get_data()
    return data.get(STATE_KEY_GAME, None)


def get_text_by_shoot_type(shoot_type: ShootType) -> str:
    if shoot_type == ShootType.HIT:
        return "Попадание"
    elif shoot_type == ShootType.DESTROY:
        return "Уничтожил"
    else:
        return "Промах"


def get_legend() -> str:
    return f"{WATER_SYMBOL} - неизвестная клетка/вода\n" \
           f"{STRIKE_WATER_SYMBOL} - попадание по воде\n" \
           f"{SHIP_SYMBOL} - палуба\n" \
           f"{STRIKE_SHIP_SYMBOL} - пораженная палуба"
