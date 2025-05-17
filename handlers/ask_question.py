# handlers/ask_question.py

from telegram import Update
from telegram.ext import ContextTypes
import services.rag_service as rag
import utils.keyboards as kb

async def handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Получает любой текст как вопрос (если он не команда) и отвечает.
    Теперь строгий контроль doc_id: если не выбран, просим выбрать.
    """
    chat_id = update.effective_chat.id
    question = update.message.text.strip()

    # Проверяем, что пользователь действительно нажал ❓ «Задать вопрос»
    if not context.user_data.get("awaiting_question"):
        await update.message.reply_text(
            "❓ Чтобы задать вопрос, сначала нажмите кнопку «❓ Задать вопрос».",
            reply_markup=kb.main_menu(),
        )
        return

    # Сейчас, когда пользователь в состоянии awaiting_question, ожидаем, что doc_id уже установлен
    doc_id = context.user_data.get("doc_id")
    if doc_id is None:
        # Нет выбранного документа
        await update.message.reply_text(
            "❗ Документ не выбран. Сначала выберите файл через 📚 «Мои документы».",
            reply_markup=kb.main_menu(),
        )
        return

    # Всё готово — обрабатываем вопрос
    answer = rag.find_answer(chat_id, doc_id, question)

    # Сброс состояния awaiting_question, но сохраняем doc_id
    context.user_data.pop("awaiting_question", None)

    await update.message.reply_text(
        answer,
        reply_markup=kb.main_menu(),
    )
