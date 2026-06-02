from aiogram import Router, types
from aiogram.filters import Command

from database import register_user
from keyboards import main_menu_keyboard
from aiogram.enums import ParseMode
parse_mode=ParseMode.HTML


router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    register_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
    )
    await message.answer(
    "<b>👋 Привет! Я — трекер привычек.</b>\n\n"
    "Помогаю вырабатывать полезные привычки и отслеживать прогресс.\n\n"
    "<b>🚀 Возможности:</b>\n"
    "➕ Создавать привычки\n"
    "✅ Отмечать выполнение\n"
    "📊 Смотреть статистику\n\n"
    "Выбери действие в меню ниже:",
    reply_markup=main_menu_keyboard(),
    parse_mode=ParseMode.HTML
    
)


@router.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "❓ <b>Помощь по командам</b>\n\n"
        "/start — Главное меню\n"
        "/help — Эта справка\n"
        "/cancel — Отменить текущее действие\n\n"
        "Также используй кнопки меню для навигации.",
        reply_markup=main_menu_keyboard(),
        parse_mode=ParseMode.HTML
    )


@router.message(Command("cancel"))
async def cmd_cancel(message: types.Message):
    await message.answer(
        "✅ Действие отменено.",
        reply_markup=main_menu_keyboard(),
    )


@router.callback_query(lambda c: c.data == "help")
async def help_callback(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "❓ <b>Помощь по командам</b>\n\n"
        "/start — Главное меню\n"
        "/help — Эта справка\n"
        "/cancel — Отменить текущее действие\n\n"
        "Также используй кнопки меню для навигации.",
        reply_markup=main_menu_keyboard(),
        parse_mode=ParseMode.HTML
    )


@router.callback_query(lambda c: c.data == "main_menu")
async def main_menu_callback(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "🏠 <b>Главное меню</b>\n\nВыбери действие:",
        reply_markup=main_menu_keyboard(),
        parse_mode=ParseMode.HTML
    )
