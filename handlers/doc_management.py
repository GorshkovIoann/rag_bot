# handlers/doc_management.py

from telegram import Update
from telegram.ext import ContextTypes
import utils.file_utils as fu
import utils.keyboards as kb

async def select_doc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, doc_id = query.data.split(":")
    context.user_data["doc_id"] = int(doc_id)
    await query.message.edit_text(
        f"✅ Документ *{doc_id}* выбран.\nТеперь нажмите ❓ «Задать вопрос» или вернитесь в меню.",
        parse_mode="Markdown",
        reply_markup=kb.back_to_menu_button()
    )

async def delete_doc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, doc_id = query.data.split(":")
    chat_id = query.message.chat.id

    # Удаляем документ
    fu.delete_doc(chat_id, int(doc_id))

    # Собираем оставшиеся
    docs = fu.list_docs(chat_id)

    if not docs:
        # Нет документов: удаляем inline-сообщение и шлём новое с main_menu
        try:
            await query.message.delete()
        except:
            pass
        await query.message.reply_text(
            "🗑️ Все документы удалены.",
            reply_markup=kb.main_menu()
        )
    else:
        # Есть документы: обновляем inline-клавиатуру
        await query.message.edit_text(
            "📚 Выберите документ:",
            reply_markup=kb.docs_list(docs)
        )
