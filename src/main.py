import asyncio
import os
import traceback
from pathlib import Path

from aiogram import Bot, Dispatcher

from src.config import BOT_TOKEN
from src.handlers.form import router


def _find_file(filename: str) -> str | None:
    base_dir = Path(__file__).parent.parent
    candidates = [
        Path(filename),
        Path("../") / filename,
        base_dir / filename,
        base_dir / "src" / filename,
    ]
    for p in candidates:
        if p.exists():
            return str(p)
    return None


async def main():
    main_docx = _find_file("Main_data1.docx")
    st_docx = _find_file("test.docx")

    if not main_docx:
        print("❌ Не найден шаблон Main_data1.docx (А–СИЗ)")
        return
    if not st_docx:
        print("❌ Не найден шаблон test.docx (С1–Т3)")
        return

    try:
        _ = os.path.getsize(main_docx)
        _ = os.path.getsize(st_docx)
    except Exception as e:
        print(f"❌ Не удалось прочитать шаблоны: {e}")
        return

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    try:
        await dp.start_polling(bot, timeout=30)
    except Exception as e:
        print(f"Ошибка при запуске бота: {e}")
        print(traceback.format_exc())


if __name__ == '__main__':
    asyncio.run(main())
