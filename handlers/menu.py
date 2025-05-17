# handlers/menu.py

from telegram import Update
from telegram.ext import ContextTypes
import utils.keyboards as kb
import utils.file_utils as fu

# States: awaiting file upload or question

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    fu.ensure_chat_dir(chat_id)
    # Reset states
    context.user_data.clear()

    await update.message.reply_text(
        "Привет! Я RAG-бот. Выберите действие:",
        reply_markup=kb.main_menu(),
    )

async def prompt_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.clear()
    context.user_data["awaiting_file"] = True
    await update.message.reply_text(
        "📄 Пожалуйста, отправьте ваш .txt файл для обработки.",
        reply_markup=kb.back_to_menu_button(),
    )

async def show_docs_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.clear()
    chat_id = update.effective_chat.id
    docs = fu.list_docs(chat_id)
    if not docs:
        await update.message.reply_text(
            "📂 Нет загруженных документов. Сначала загрузите файл.",
            reply_markup=kb.back_to_menu_button(),
        )
    else:
        await update.message.reply_text(
            "📚 Выберите документ:",
            reply_markup=kb.docs_list(docs),
        )

async def prompt_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Сохраняем уже выбранный doc_id, если есть
    old_doc_id = context.user_data.get("doc_id")
    context.user_data.clear()
    if old_doc_id is not None:
        context.user_data["doc_id"] = old_doc_id
    context.user_data["awaiting_question"] = True

    await update.message.reply_text(
        "❓ Отлично! Теперь введите ваш вопрос.",
        reply_markup=kb.back_to_menu_button(),
    )

async def detect_genre_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🎭 Функция определения жанра пока не реализована.",
        reply_markup=kb.back_to_menu_button(),
    )

async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "back_to_menu":
        # send new main menu
        await query.message.reply_text(
            "Главное меню:",
            reply_markup=kb.main_menu(),
        )
    else:
        # let other handlers manage select_doc
        return