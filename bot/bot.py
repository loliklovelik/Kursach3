import asyncio

from aiogram import Bot, Dispatcher

from bot.router import router

# todo insert your bot token
bot = Bot(token="")
dp = Dispatcher()


# use for start bot
def main() -> None:
    asyncio.run(start_bot())


async def start_bot() -> None:
    dp.include_router(router)
    await dp.start_polling(bot)
