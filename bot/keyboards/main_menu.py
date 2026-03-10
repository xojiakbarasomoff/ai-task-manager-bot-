from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_menu() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📁 Loyihalarim"),
                KeyboardButton(text="✅ Vazifalarim"),
            ],
            [
                KeyboardButton(text="➕ Loyiha yaratish"),
                KeyboardButton(text="📝 Vazifa yaratish"),
            ],
            [
                KeyboardButton(text="🤖 AI Vazifalar"),
                KeyboardButton(text="📊 Statistika"),
            ],
        ],
        resize_keyboard=True,
        input_field_placeholder="Amalni tanlang...",
    )
    return keyboard