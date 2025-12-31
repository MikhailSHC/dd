import asyncio
import os
import traceback

from aiogram import Bot, Dispatcher

from src.config import BOT_TOKEN
from src.handlers.form import router


async def main():

    # Проверяем существование файла шаблона
    template_path = "../Main_data.pdf"
    if not os.path.exists(template_path):
        # Пробуем найти в корне проекта
        from pathlib import Path
        base_dir = Path(__file__).parent.parent
        template_path = base_dir / "Main_data.pdf"

    if os.path.exists(template_path):
        file_size = os.path.getsize(template_path)
    else:
        return

    template_path_2 = "../test.docx"
    if not os.path.exists(template_path_2):
        from pathlib import Path
        base_dir = Path(__file__).parent.parent
        template_path_2 = base_dir / "test.docx"

    if os.path.exists(template_path_2):
        file_size_2 = os.path.getsize(template_path_2)
    else:
        return

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    try:
        await dp.start_polling(bot,timeout=30)
    except Exception as e:
        print(f"Ошибка при запуске бота: {e}")
        print(traceback.format_exc())


if __name__ == '__main__':
    asyncio.run(main())