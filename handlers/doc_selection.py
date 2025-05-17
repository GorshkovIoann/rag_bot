# handlers/doc_selection.py

from telegram import Update
from telegram.ext import ContextTypes
import utils.keyboards as kb

async def select_doc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    _, doc_id = query.data.split(":")
    context.user_data["doc_id"] = int(doc_id)

    await query.edit_message_text(
        f"📄 Документ *{doc_id}* выбран.\nТеперь введите ваш вопрос.",
        parse_mode="Markdown",
        reply_markup=kb.back_to_menu_button(),
    )
