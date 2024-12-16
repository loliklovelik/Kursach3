from aiogram import Router, F, Bot
from aiogram.enums import ParseMode
from aiogram.filters.command import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.keyboard import start_menu, exit_kb
from bot.SessionStep import SessionStep, STATE_KEY_GAME
from bot.utils import get_game_from_state, send_message_and_set_state_to_user, send_message_to_user, \
    get_text_by_shoot_type, get_legend
from bot.constatns import END_GAME_BUTTON, START_GAME_BUTTON, JOIN_GAME_BUTTON
from core.game import generate_game, join_to_game, generate_playing_field, check_shoot_coordinates, end_game
from models.Game import Game
from models.ShootType import ShootType
from models.User import from_aiogram_user

router = Router()


@router.message(CommandStart())
async def command_start_handler(msg: Message, state: FSMContext) -> None:
    await state.set_state(SessionStep.menu)
    await msg.answer("Привет, начнем игру?", reply_markup=start_menu)


@router.message(Command("menu"))
@router.message(F.text == "Меню")
@router.message(F.text == END_GAME_BUTTON)
async def menu_handler(msg: Message, state: FSMContext, bot: Bot) -> None:
    user = from_aiogram_user(msg.from_user)

    # end game if needed
    game = await get_game_from_state(state)
    if game is not None:
        other_user = game.other_user(user)
        await send_message_and_set_state_to_user(
            bot=bot,
            storage=state.storage,
            user=other_user,
            message=f"@{user.username} Вышел из игры",
            state=SessionStep.menu,
            new_data={},
            reply_markup=start_menu,
        )
        await end_game(game.id)

    await state.set_state(SessionStep.menu)
    await state.set_data({})
    await msg.answer("Меню", reply_markup=start_menu)


@router.message(F.text == START_GAME_BUTTON)
async def start_game_handler(msg: Message, state: FSMContext) -> None:
    game = await generate_game(from_aiogram_user(msg.from_user))
    await state.set_state(SessionStep.starting_game)
    await state.set_data({STATE_KEY_GAME: game})
    await msg.answer(
        f"Игра создана, ждем подключения второго игрока, "
        f"для этого отправь ему id игры(копируется нажатием): `{game.id}`",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=exit_kb,
    )


@router.message(F.text == JOIN_GAME_BUTTON)
async def join_game_handler(msg: Message, state: FSMContext) -> None:
    await state.set_state(SessionStep.joining_to_game)
    await msg.answer("Пришли сюда id игры", reply_markup=exit_kb)


@router.message(SessionStep.joining_to_game, F.text)
async def enter_game_id_handler(msg: Message, state: FSMContext, bot: Bot) -> None:
    user = from_aiogram_user(msg.from_user)
    game = await join_to_game(msg.text, user)
    if game is None:
        await msg.answer("Неверный id игры", reply_markup=exit_kb)
        return

    await state.set_state(SessionStep.in_game)
    await state.set_data({STATE_KEY_GAME: game})

    other_user = game.other_user(user)
    await send_message_and_set_state_to_user(
        bot=bot,
        storage=state.storage,
        user=other_user,
        message=f"К вам подключился @{user.username}",
        state=SessionStep.in_game,
    )
    await msg.answer(f"Вы в игре c @{other_user.username}", reply_markup=exit_kb)

    # generate ships
    await send_message_to_user(
        bot=bot,
        user=other_user,
        message="Генерируем игровое поле...",
    )
    await msg.answer("Генерируем игровое поле...")
    await generate_playing_field(game)

    await send_message_to_user(
        bot=bot,
        user=other_user,
        message=f"Ваше игровое поле\n{game.playing_field(other_user)}",
        parse_mode=ParseMode.MARKDOWN,
    )
    await send_message_to_user(
        bot=bot,
        user=other_user,
        message=get_legend(),
    )

    await msg.answer(f"Ваше игровое поле\n{game.playing_field(user)}", parse_mode=ParseMode.MARKDOWN)
    await msg.answer(get_legend())

    await send_your_step(
        bot=bot,
        game=game,
    )


@router.message(SessionStep.in_game, F.text)
async def in_game_handler(msg: Message, state: FSMContext, bot: Bot) -> None:
    user = from_aiogram_user(msg.from_user)
    game = await get_game_from_state(state)
    other_user = game.other_user(user)
    other_playing_field = game.playing_field(other_user)
    coordinates = msg.text

    # validate input
    if not game.is_user_step(user):
        await msg.answer("Сейчас ход соперника")
        return
    if not check_shoot_coordinates(coordinates):
        await msg.answer("Неверные координаты. Повторите попытку")
        return
    if not other_playing_field.can_shoot(coordinates):
        await msg.answer("Вы туда уже стреляли. Повторите попытку")
        return

    shoot_type = await other_playing_field.shoot(coordinates)

    await msg.answer(f"Вы сходили {coordinates}", reply_markup=exit_kb)
    await msg.answer(get_text_by_shoot_type(shoot_type), reply_markup=exit_kb)

    await send_message_to_user(
        bot=bot,
        user=other_user,
        message=f"Противник сходил {coordinates}",
    )
    await send_message_to_user(
        bot=bot,
        user=other_user,
        message=get_text_by_shoot_type(shoot_type),
    )
    await send_message_to_user(
        bot=bot,
        user=other_user,
        message=f"Ваше игровое поле\n{other_playing_field}",
        parse_mode=ParseMode.MARKDOWN,
    )

    if other_playing_field.check_win():
        await state.set_state(SessionStep.menu)
        await state.set_data({})
        await msg.answer("Вы выйграли!", reply_markup=start_menu)
        await send_message_and_set_state_to_user(
            bot=bot,
            storage=state.storage,
            user=other_user,
            message=f"@{user.username} победил",
            state=SessionStep.menu,
            new_data={},
            reply_markup=start_menu,
        )
        await end_game(game.id)
        return

    # change active player if missed
    if shoot_type == ShootType.MISS:
        await msg.answer("Ход соперника")
        game.next_step()

    await send_your_step(
        bot=bot,
        game=game,
    )


# fallback
@router.message(F.text)
async def fallback_handler(msg: Message) -> None:
    await msg.answer("Неверное сообщение")


async def send_your_step(
        bot: Bot,
        game: Game,
) -> None:
    await send_message_to_user(
        bot=bot,
        user=game.step_user,
        message="Ваш ход",
    )
    other_user = game.other_user(game.step_user)
    await send_message_to_user(
        bot=bot,
        user=game.step_user,
        message=f"Игровое поле соперника\n{game.playing_field(other_user).blured()}",
        parse_mode=ParseMode.MARKDOWN,
    )
