
import nltk
nltk.download('punkt_tab')
# handlers/file_upload.py

import logging
from pathlib import Path
from telegram import Update
from telegram.ext import ContextTypes
import utils.file_utils as fu
import utils.convert_utils as cu
import services.rag_service as rag
import utils.keyboards as kb

logger = logging.getLogger(__name__)

async def upload_txt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Универсальный хендлер для загрузки файлов:
    1) Проверяет состояние awaiting_file
    2) Скачивает исходный файл
    3) Конвертирует в текст (txt/pdf/docx/jpg/png)
    4) Сохраняет извлечённый текст в raw_texts как .txt
    5) Индексирует текст в RAG
    6) Уведомляет пользователя о ходе и результате
    """
    chat_id = update.effective_chat.id

    # 1) Проверяем, что бот ждёт файл
    if not context.user_data.get("awaiting_file"):
        await update.message.reply_text(
            "❗ Чтобы загрузить файл, сначала нажмите «📄 Загрузить файл».",
            reply_markup=kb.main_menu(),
        )
        return

    doc = update.message.document
    ext = doc.file_name.rsplit(".", 1)[-1].lower()
    logger.info("Получен файл %s (ext=%s, size=%d)", doc.file_name, ext, doc.file_size)

    # 2) Скачиваем исходный файл
    try:
        file_obj = await doc.get_file()
        data = await file_obj.download_as_bytearray()
        logger.debug("Скачано %d байт", len(data))
    except Exception as e:
        logger.error("Не удалось скачать файл: %s", e, exc_info=True)
        await update.message.reply_text(
            "❗ Ошибка при скачивании файла. Попробуйте ещё раз.",
            reply_markup=kb.main_menu(),
        )
        return

    # 3) Конвертируем в текст
    try:
        if ext == "txt":
            text = data.decode("utf-8", errors="ignore")
        elif ext == "pdf":
            logger.info("Конвертация PDF → текст")
            text = cu.pdf_to_text(data)
        elif ext == "docx":
            logger.info("Конвертация DOCX → текст")
            text = cu.docx_to_text(data)
        elif ext in {"jpg", "jpeg", "png"}:
            logger.info("OCR изображения → текст")
            text = cu.image_to_text(data)
        else:
            logger.warning("Неподдерживаемый формат: .%s", ext)
            await update.message.reply_text(
                f"❗ Формат *.{ext}* не поддерживается.",
                parse_mode="Markdown",
                reply_markup=kb.main_menu(),
            )
            return
        logger.debug(
            "Текст после конвертации (первые 100 символов): %r",
            text[:100].replace("\n", " ")
        )
    except Exception as e:
        logger.error("Ошибка конвертации %s: %s", ext, e, exc_info=True)
        await update.message.reply_text(
            "❗ Не удалось извлечь текст из файла. Попробуйте другой формат.",
            reply_markup=kb.main_menu(),
        )
        return

    # 4) Генерируем doc_id и сохраняем извлечённый текст как .txt
    doc_id = fu.next_doc_id(chat_id)
    try:
        raw_dir = fu.ensure_chat_dir(chat_id) / "raw_texts"
        base_name = Path(doc.file_name).stem
        txt_path = raw_dir / f"{doc_id}_{base_name}.txt"
        txt_path.write_text(text, encoding="utf-8")
        logger.info("Сохранён текстовый файл: %s", txt_path)
    except Exception as e:
        logger.error("Ошибка сохранения .txt: %s", e, exc_info=True)
        await update.message.reply_text(
            "❗ Ошибка при сохранении текстового файла.",
            reply_markup=kb.main_menu(),
        )
        return

    # 5) Уведомляем пользователя о начале обработки
    status = await update.message.reply_text(
        "⏳ Начинаю обработку документа, это может занять несколько секунд…",
        reply_markup=None
    )

    # 6) Индексируем текст в RAG
    try:
        logger.info("upload_txt: calling process_text for doc_id=%d", doc_id)
        rag.process_text(chat_id, text, doc.file_name, doc_id)
        logger.info("upload_txt: process_text returned for doc_id=%d", doc_id)
    except Exception as e:
        logger.error("upload_txt: process_text error: %s", e, exc_info=True)
        await status.edit_text(
            "❗ Не удалось обработать документ. Попробуйте позже.",
            reply_markup=None
        )
        # После ошибки сбрасываем меню
        await update.message.reply_text("Главное меню:", reply_markup=kb.main_menu())
        return

    # 7) Сбрасываем состояние ожидания и запоминаем текущий документ
    context.user_data.clear()
    context.user_data["doc_id"] = doc_id

    # 8) Обновляем статус-сообщение без ReplyKeyboardMarkup
    await status.edit_text(f"✅ Документ #{doc_id} готов к вопросам!")

    # 9) Посылаем отдельное сообщение с main_menu
    await update.message.reply_text(
        "Выберите действие:",
        reply_markup=kb.main_menu()
    )
