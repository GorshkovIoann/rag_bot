````markdown
# RAG Telegram Bot

**Self-service Retrieval-Augmented Generation (RAG)** бот в Telegram, позволяющий загружать тексты (TXT, PDF, DOCX, JPG/PNG), автоматически конвертировать их в plain-text, сегментировать, векторизовать и отвечать на вопросы по загруженным документам.

---

##  Возможности

- Загрузка и конвертация:
  - **TXT** → сохраняется как есть  
  - **PDF** → извлечение текста через `pdfminer`/`poppler-utils`  
  - **DOCX** → через `python-docx`  
  - **JPG/PNG** → OCR через `pytesseract` + `tesseract-ocr`  
- Сегментация текста на предложения и фрагменты (батчи по 50 слов)  
- Векторизация фрагментов через модель **FRIDA** (`T5EncoderModel`)  
- Хранение сегментов (`segments.pkl`) и эмбеддингов (`vectors.npz`)  
- Поиск релевантных фрагментов по вопросу (косинусная близость)  
- “Human-friendly” ответ через OpenRouter API + модель Gemini-2.0  
- Управление несколькими документами:
  - Просмотр списка  
  - Удаление одного документа  
  - Полная очистка (с сохранением структуры папки)  
- Прогресс-бар в чате при векторизации  
- Поддержка GPU (через `nvidia/cuda` образ)  

---

##  Предварительные требования

- Docker ≥ 20.10 + NVIDIA Container Toolkit (для GPU)  
- `tesseract-ocr` (+ языковые пакеты, напр. `tesseract-ocr-rus`)  
- Telegram Bot API токен  
- OpenRouter API ключ (для Gemini)  

---

##  Установка и запуск

1. **Склонируйте репозиторий**  
   ```bash
   git clone https://github.com/your-repo/rag-telegram-bot.git
   cd rag-telegram-bot
````

2. **Создайте файл `.env`** в корне:

   ```dotenv
   TELEGRAM_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
   OPENROUTER_API_KEY=sk-or-v1-...
   DEVICE=cuda                  # или cpu
   DATA_DIR=data
   BATCH_SIZE=64                # размер батча векторизации
   SEGMENT_SIZE=50
   ```

3. **Постройте и запустите контейнеры**

   ```bash
   docker compose build --no-cache
   docker compose up -d
   ```

4. **Проверьте логи**

   ```bash
   docker compose logs -f bot
   ```

5. **Откройте бот в Telegram** и нажмите **/start**.

---

## Структура проекта

```
.
├── bot.py                  # Точка входа, настройка хэндлеров
├── handlers/               # Обработчики команд и сообщений
│   ├── menu.py
│   ├── file_upload.py
│   ├── doc_selection.py
│   ├── ask_question.py
│   └── misc.py
├── services/               # Бизнес-логика RAG
│   ├── rag_service.py
│   └── segmenter.py
├── utils/                  # Утилиты работы с файлами, конвертации, клавиатуры
│   ├── file_utils.py
│   ├── convert_utils.py
│   └── keyboards.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

##  Использование

1. **/start** — вывести главное меню
2. **📄 Загрузить файл** — отправьте документ (TXT/PDF/DOCX/JPG/PNG)
3. **📚 Мои документы** — выбор и удаление загруженных файлов
4. **❓ Задать вопрос** — введите свой запрос по последнему документу
5. **🗑️ Очистить данные** — удалить все загруженные документы и индексы

---

##  Основные библиотеки

| Библиотека            | Назначение                                |
| --------------------- | ----------------------------------------- |
| `python-telegram-bot` | Фреймворк Telegram Bot API                |
| `transformers`        | Токенизация и энкодер T5 (FRIDA)          |
| `torch`               | PyTorch для моделей и GPU                 |
| `nltk`                | Разбиение текста на предложения           |
| `poppler-utils`       | PDF → текст                               |
| `python-docx`         | DOCX → текст                              |
| `pytesseract`         | OCR изображений                           |
| `tesseract-ocr-rus`   | Русский пакет OCR                         |
| `numpy`               | Векторные операции, сохранение `.npz`     |
| `pickle`              | Сериализация сегментов                    |
| `httpx`               | HTTP-клиент для Telegram и OpenRouter API |

---

##  Развитие и идеи

* Интеграция с внешними хранилищами (S3, Google Drive)
* Детекция жанра текста (нейросеть под вашу реализацию)
* Мульти-чтение и параллельная обработка
* Веб-интерфейс для аналитики и просмотра сегментов
