import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()  


# Telegram bot token (set this environment variable before running)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "7783033449:AAGBh3R4SyFjvQJElVl6-1pcpPdOykLzVuQ")

# Base project directory
BASE_DIR = Path(__file__).parent

# Directory for storing user data (per-chat state)
DATA_DIR = BASE_DIR / "data"

# Allowed file extensions for upload
ALLOWED_EXTENSIONS = {".txt"}

# Segmenter settings
SEGMENT_SIZE = 50
USE_STUDENT = False  # switch to distilled model when True
STUDENT_CKPT = BASE_DIR / "models" / "mini_frida.pt"
# config.py, в разделе DEVICE
DEVICE = os.getenv("DEVICE", "cpu").lower()
if DEVICE != "cuda":
    DEVICE = "cpu"


# LLM judge settings (OpenRouter)
API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = os.getenv("OPENROUTER_API_KEY", "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")
MODEL = "google/gemini-2.0-flash-001"

# Telegram polling settings
POLLING_TIMEOUT = 20  # seconds

# Ensure data directory exists
data_dir = DATA_DIR
if not data_dir.exists():
    data_dir.mkdir(parents=True, exist_ok=True)
