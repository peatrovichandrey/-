from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Мои привычки", callback_data="list_habits")],
        [InlineKeyboardButton(text="➕ Новая привычка", callback_data="new_habit")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="show_stats")],
        [InlineKeyboardButton(text="❓ Помощь", callback_data="help")],
    ])


def habit_actions_keyboard(habit_id: int, is_completed: bool) -> InlineKeyboardMarkup:
    buttons = []

    if is_completed:
        buttons.append([InlineKeyboardButton(text="↩️ Отменить", callback_data=f"uncheck_{habit_id}")])
    else:
        buttons.append([InlineKeyboardButton(text="✅ Выполнено", callback_data=f"check_{habit_id}")])

    buttons.append([InlineKeyboardButton(text="📊 Статистика", callback_data=f"stats_{habit_id}")])
    buttons.append([InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"edit_{habit_id}")])
    buttons.append([InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete_{habit_id}")])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="list_habits")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def habits_list_keyboard(habits) -> InlineKeyboardMarkup:
    buttons = []
    for h in habits:
        buttons.append([InlineKeyboardButton(
            text=f"{'✅' if h.get('completed', False) else '⬜'} {h['name']}",
            callback_data=f"view_{h['id']}",
        )])
    buttons.append([InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def frequency_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Ежедневно", callback_data="freq_daily")],
        [InlineKeyboardButton(text="📆 Еженедельно", callback_data="freq_weekly")],
        [InlineKeyboardButton(text="🔙 Отмена", callback_data="main_menu")],
    ])


def confirm_delete_keyboard(habit_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗑 Да, удалить", callback_data=f"confirm_delete_{habit_id}")],
        [InlineKeyboardButton(text="🔙 Нет, назад", callback_data=f"view_{habit_id}")],
    ])


def back_to_habit_keyboard(habit_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data=f"view_{habit_id}")],
    ])
