import json
import os
from aiogram import Bot
from dotenv import load_dotenv
from aiogram.client.default import DefaultBotProperties

load_dotenv()  # Загружаем переменные из .env

BOT_TOKEN = os.getenv("token")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не загружен. Проверьте ваш файл .env")

bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MESSAGES = json.load(open(os.path.join(BASE_DIR, "../texts/message.json"), encoding="utf-8"))
BUTTONS = json.load(open(os.path.join(BASE_DIR, "../texts/button.json"), encoding="utf-8"))

PATH_TO_PHOTO = "/data/res/leomax.jpg"

ADMINS = ["NahaPych","vanek_forest"]

TOKEN_WALLET = os.getenv("token_wallet")
RECEIVER = os.getenv("receiver")