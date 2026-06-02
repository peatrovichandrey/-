from datetime import date, timedelta
from typing import Set

from database import is_habit_completed_today


def get_streak(completed_dates: Set[str], frequency: str) -> int:
    """Рассчитывает текущую серию (streak) выполненных дней/недель."""
    if not completed_dates:
        return 0

    sorted_dates = sorted(completed_dates, reverse=True)
    today = date.today()

    if frequency == "daily":
        return _get_daily_streak(sorted_dates, today)
    else:
        return _get_weekly_streak(sorted_dates, today)


def _get_daily_streak(sorted_dates: list, today: date) -> int:
    streak = 0
    check_date = today

    if today.isoformat() not in sorted_dates:
        yesterday = today - timedelta(days=1)
        if yesterday.isoformat() not in sorted_dates:
            return 0
        check_date = yesterday

    while check_date.isoformat() in sorted_dates:
        streak += 1
        check_date -= timedelta(days=1)

    return streak


def _get_weekly_streak(sorted_dates: list, today: date) -> int:
    streak = 0
    current_week_start = today - timedelta(days=today.weekday())

    if current_week_start.isoformat() not in sorted_dates:
        prev_week = current_week_start - timedelta(weeks=1)
        if prev_week.isoformat() not in sorted_dates:
            return 0
        current_week_start = prev_week

    while current_week_start.isoformat() in sorted_dates:
        streak += 1
        current_week_start -= timedelta(weeks=1)

    return streak


def get_completion_rate(completed_dates: Set[str], frequency: str, days: int = 30) -> float:
    """Процент выполнения за последние N дней/недель."""
    today = date.today()

    if frequency == "daily":
        total = days
    else:
        total = max(days // 7, 1)

    count = 0
    for i in range(total):
        if frequency == "daily":
            d = today - timedelta(days=i)
        else:
            d = today - timedelta(weeks=i)
            d = d - timedelta(days=d.weekday())
        if d.isoformat() in completed_dates:
            count += 1

    return round((count / total) * 100) if total > 0 else 0


def get_week_dates() -> list:
    """Возвращает список дат текущей недели (Пн-Вс)."""
    today = date.today()
    start = today - timedelta(days=today.weekday())
    return [start + timedelta(days=i) for i in range(7)]


def get_habit_status_emoji(is_completed: bool) -> str:
    return "✅" if is_completed else "⬜"


def format_habit_list(habits, today: date) -> str:
    """Форматирует список привычек для отображения."""
    if not habits:
        return "У вас пока нет привычек."

    lines = []
    for h in habits:
        completed = is_habit_completed_today(h["id"], today)
        emoji = get_habit_status_emoji(completed)
        freq = "📅" if h["frequency"] == "daily" else "📆"
        lines.append(f"{emoji} {freq} <b>{h['name']}</b>")
        if h["description"]:
            lines.append(f"   <i>{h['description']}</i>")
    return "\n".join(lines)
