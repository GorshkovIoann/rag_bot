# utils/keyboards.py

from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_menu() -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton("📄 Загрузить файл")],
        [KeyboardButton("📚 Мои документы"), KeyboardButton("❓ Задать вопрос")],
        [KeyboardButton("🗑️ Очистить данные"), KeyboardButton("🎭 Определить жанр")],
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

def docs_list(docs: list[tuple[int, str]]) -> InlineKeyboardMarkup:
    kb = []
    for doc_id, name in docs:
        # определяем иконку по расширению
        ext = name.rsplit(".", 1)[-1].lower()
        icon = {
            "txt": "📄", "pdf": "📕", "docx": "📗",
            "jpg": "🖼️", "jpeg": "🖼️", "png": "🖼️"
        }.get(ext, "📁")
        kb.append([
            InlineKeyboardButton(f"{icon} {name}", callback_data=f"select_doc:{doc_id}"),
            InlineKeyboardButton("❌", callback_data=f"delete_doc:{doc_id}")
        ])
    kb.append([InlineKeyboardButton("◀️ Назад", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(kb)


def back_to_menu_button(text: str = "◀️ Назад") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton(text, callback_data="back_to_menu")]])
