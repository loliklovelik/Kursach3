from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from bot.constatns import JOIN_GAME_BUTTON, START_GAME_BUTTON, END_GAME_BUTTON

start_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=START_GAME_BUTTON)],
        [KeyboardButton(text=JOIN_GAME_BUTTON)],
    ],
    resize_keyboard=True,
)

exit_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=END_GAME_BUTTON)]], resize_keyboard=True)
