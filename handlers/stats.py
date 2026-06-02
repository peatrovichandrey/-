from aiogram import Router, types, F

from database import get_habit, get_habit_stats, get_habits, is_habit_completed_today
from keyboards import main_menu_keyboard, back_to_habit_keyboard, habit_actions_keyboard
from utils import get_streak, get_completion_rate
from datetime import date
from aiogram.enums import ParseMode

router = Router()


@router.callback_query(F.data == "show_stats")
async def show_all_stats(callback: types.CallbackQuery):
    await callback.answer()
    habits = get_habits(callback.from_user.id)

    if not habits:
        await callback.message.edit_text(
            "📊 Статистика\n\nУ вас пока нет привычек.",
            reply_markup=main_menu_keyboard(),
        )
        return

    lines = ["📊 Общая статистика\n"]
    today = date.today()

    for h in habits:
        stats = get_habit_stats(h["id"])
        if not stats:
            continue

        streak = get_streak(stats["completed_dates"], stats["frequency"])
        rate = get_completion_rate(stats["completed_dates"], stats["frequency"], 30)
        completed_today = is_habit_completed_today(h["id"], today)
        emoji = "✅" if completed_today else "⬜"

        lines.append(
            f"{emoji} <b>{h['name']}</b>\n"
            f"   🔥 Серия: {streak} {'дн.' if stats['frequency'] == 'daily' else 'нед.'}\n"
            f"   📊 За 30 дней: {rate}%"
        )

    await callback.message.edit_text(
        "\n".join(lines),
        reply_markup=main_menu_keyboard(),
    )


@router.callback_query(F.data.startswith("stats_"))
async def show_habit_stats(callback: types.CallbackQuery):
    await callback.answer()
    habit_id = int(callback.data.split("_")[1])
    habit = get_habit(habit_id)
    stats = get_habit_stats(habit_id)

    if not habit or not stats:
        await callback.message.edit_text("❌ Привычка не найдена.")
        return

    streak = get_streak(stats["completed_dates"], stats["frequency"])
    rate_7 = get_completion_rate(stats["completed_dates"], stats["frequency"], 7)
    rate_30 = get_completion_rate(stats["completed_dates"], stats["frequency"], 30)
    total = len(stats["completed_dates"])
    freq_text = "дней" if stats["frequency"] == "daily" else "недель"

    today = date.today()
    completed_today = is_habit_completed_today(habit_id, today)
    status_text = "✅ выполнено сегодня" if completed_today else "⬜ ещё не выполнено"

    text = (
        f"📊 <b>Статистика: {habit['name']}</b>\n\n"
        f"📌 Статус: {status_text}\n"
        f"🔥 Текущая серия: <b>{streak}</b> {freq_text}\n"
        f"📊 За 7 дней: <b>{rate_7}%</b>\n"
        f"📊 За 30 дней: <b>{rate_30}%</b>\n"
        f"📈 Всего отметок: <b>{total}</b>\n"
    )
    parse_mode=ParseMode.HTML

    await callback.message.edit_text(
        text,
        reply_markup=habit_actions_keyboard(habit_id, completed_today),
    )
