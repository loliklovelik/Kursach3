from aiogram.fsm.state import StatesGroup, State

STATE_KEY_GAME = "game"


class SessionStep(StatesGroup):
    menu = State()
    joining_to_game = State()
    starting_game = State()
    in_game = State()
