# bot.py

import logging
from telegram import __version__ as TG_VER
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,  # теперь INFO и выше
)
logger = logging.getLogger(__name__)

try:
    from telegram import Update
    from telegram.ext import (
        ApplicationBuilder,
        CommandHandler,
        MessageHandler,
        CallbackQueryHandler,
        ContextTypes,
        filters,
    )
except ImportError:
    raise RuntimeError("Установите python-telegram-bot>=20.0")

import config
from handlers import doc_management, menu, file_upload, doc_selection, ask_question, misc

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Ошибка: %s", context.error)


def main() -> None:
    app = (
        ApplicationBuilder()
        .token(config.TELEGRAM_TOKEN)
        .build()
    )

    # /start
    app.add_handler(CommandHandler("start", menu.start))

    app.add_handler(CallbackQueryHandler(doc_management.select_doc, pattern=r"^select_doc:"))
    app.add_handler(CallbackQueryHandler(doc_management.delete_doc, pattern=r"^delete_doc:"))


    # Reply keyboard actions
    app.add_handler(MessageHandler(filters.Regex(r"^📄 Загрузить файл$"), menu.prompt_upload))
    app.add_handler(MessageHandler(filters.Regex(r"^📚 Мои документы$"), menu.show_docs_text))
    app.add_handler(MessageHandler(filters.Regex(r"^❓ Задать вопрос$"), menu.prompt_question))
    app.add_handler(MessageHandler(filters.Regex(r"^🗑️ Очистить данные$"), misc.clear_data))
    app.add_handler(MessageHandler(filters.Regex(r"^🎭 Определить жанр$"), menu.detect_genre_text))

    # Inline callbacks
    app.add_handler(CallbackQueryHandler(menu.menu_callback))
    app.add_handler(CallbackQueryHandler(doc_selection.select_doc, pattern=r"^select_doc:"))

    # Upload any document (we'll внутри смотреть расширение)
    app.add_handler(
        MessageHandler(filters.Document.ALL, file_upload.upload_txt)
    )

    # Ask question
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, ask_question.handle_question)
    )

    app.add_error_handler(error_handler)

    app.run_polling(timeout=config.POLLING_TIMEOUT)


if __name__ == "__main__":
    main()
