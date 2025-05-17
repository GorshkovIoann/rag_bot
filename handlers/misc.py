# handlers/misc.py

from telegram import Update
from telegram.ext import ContextTypes
import utils.file_utils as fu
import utils.keyboards as kb

async def clear_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    fu.clear_chat_data(chat_id)
    context.user_data.clear()
    await update.message.reply_text(
        "🗑️ Все данные очищены.", reply_markup=kb.main_menu()
    )
