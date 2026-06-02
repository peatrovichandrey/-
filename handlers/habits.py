from aiogram import Router, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import (
    add_habit,
    get_habits,
    get_habit,
    update_habit,
    delete_habit,
    log_habit,
    unlog_habit,
    is_habit_completed_today,
)
from keyboards import (
    habit_actions_keyboard,
    habits_list_keyboard,
    frequency_keyboard,
    confirm_delete_keyboard,
    main_menu_keyboard,
    back_to_habit_keyboard,
)
from utils import format_habit_list, get_habit_status_emoji
from datetime import date

router = Router()


class HabitForm(StatesGroup):
    name = State()
    description = State()
    frequency = State()


class EditHabitForm(StatesGroup):
    name = State()
    description = State()
    frequency = State()


@router.callback_query(F.data == "list_habits")
async def list_habits(callback: types.CallbackQuery):
    await callback.answer()
    habits = get_habits(callback.from_user.id)
    today = date.today()

    if not habits:
        await callback.message.edit_text(
            "📋 <b>Ваши привычки</b>\n\nУ вас пока нет привычек.\nНажми «➕ Новая привычка», чтобы создать первую!",
            reply_markup=main_menu_keyboard(),
        )
        return

    habit_list = []
    for h in habits:
        completed = is_habit_completed_today(h["id"], today)
        habit_list.append({"id": h["id"], "name": h["name"], "completed": completed})

    await callback.message.edit_text(
        "📋 <b>Ваши привычки</b>\n\nНажми на привычку, чтобы открыть:",
        reply_markup=habits_list_keyboard(habit_list),
    )


@router.callback_query(F.data.startswith("view_"))
async def view_habit(callback: types.CallbackQuery):
    await callback.answer()
    habit_id = int(callback.data.split("_")[1])

    if habit_id == 0:
        await callback.message.edit_text(
            "🏠 <b>Главное меню</b>\n\nВыбери действие:",
            reply_markup=main_menu_keyboard(),
        )
        return

    habit = get_habit(habit_id)

    if not habit:
        await callback.message.edit_text("❌ Привычка не найдена.")
        return

    today = date.today()
    completed = is_habit_completed_today(habit_id, today)
    emoji = get_habit_status_emoji(completed)
    freq_text = "ежедневно" if habit["frequency"] == "daily" else "еженедельно"

    text = (
        f"{emoji} <b>{habit['name']}</b>\n\n"
        f"{'✅ <i>Выполнено сегодня</i>' if completed else '⬜ <i>Ещё не выполнено</i>'}\n"
        f"📅 Периодичность: {freq_text}\n"
    )
    if habit["description"]:
        text += f"📝 Описание: {habit['description']}\n"

    await callback.message.edit_text(
        text,
        reply_markup=habit_actions_keyboard(habit_id, completed),
    )


@router.callback_query(F.data == "new_habit")
async def new_habit_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(HabitForm.name)
    await callback.message.edit_text(
        "➕ <b>Новая привычка</b>\n\nВведите <b>название</b> привычки:",
        reply_markup=back_to_habit_keyboard(0),
    )


@router.message(StateFilter(HabitForm.name))
async def new_habit_name(message: types.Message, state: FSMContext):
    name = message.text.strip()
    if len(name) > 100:
        await message.answer("❌ Название слишком длинное (макс. 100 символов). Попробуйте снова:")
        return

    await state.update_data(name=name)
    await state.set_state(HabitForm.description)
    await message.answer(
        f"✏️ <b>{name}</b>\n\nТеперь введите <b>описание</b> (или отправьте «-», чтобы пропустить):",
        reply_markup=back_to_habit_keyboard(0),
    )


@router.message(StateFilter(HabitForm.description))
async def new_habit_description(message: types.Message, state: FSMContext):
    desc = message.text.strip()
    if desc == "-":
        desc = ""
    if len(desc) > 300:
        await message.answer("❌ Описание слишком длинное (макс. 300 символов). Попробуйте снова:")
        return

    await state.update_data(description=desc)
    await state.set_state(HabitForm.frequency)
    await message.answer(
        "📅 Выберите <b>периодичность</b>:",
        reply_markup=frequency_keyboard(),
    )


@router.callback_query(StateFilter(HabitForm.frequency), F.data.startswith("freq_"))
async def new_habit_frequency(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    freq = callback.data.split("_")[1]
    data = await state.get_data()

    habit_id = add_habit(
        user_id=callback.from_user.id,
        name=data["name"],
        description=data.get("description", ""),
        frequency=freq,
    )
    await state.clear()

    freq_text = "ежедневно" if freq == "daily" else "еженедельно"
    await callback.message.edit_text(
        f"✅ <b>Привычка создана!</b>\n\n"
        f"📌 {data['name']}\n"
        f"📅 {freq_text}\n"
        f"📝 {data.get('description', 'без описания')}",
        reply_markup=habit_actions_keyboard(habit_id, False),
    )


@router.callback_query(F.data.startswith("check_"))
async def check_habit(callback: types.CallbackQuery):
    await callback.answer()
    habit_id = int(callback.data.split("_")[1])
    today = date.today()
    log_habit(habit_id, today)

    habit = get_habit(habit_id)
    if habit:
        await callback.message.edit_text(
            f"✅ <b>{habit['name']}</b>\n\nОтмечено как выполненное!",
            reply_markup=habit_actions_keyboard(habit_id, True),
        )


@router.callback_query(F.data.startswith("uncheck_"))
async def uncheck_habit(callback: types.CallbackQuery):
    await callback.answer()
    habit_id = int(callback.data.split("_")[1])
    today = date.today()
    unlog_habit(habit_id, today)

    habit = get_habit(habit_id)
    if habit:
        await callback.message.edit_text(
            f"↩️ <b>{habit['name']}</b>\n\nОтметка отменена.",
            reply_markup=habit_actions_keyboard(habit_id, False),
        )


@router.callback_query(F.data.startswith("delete_"))
async def delete_habit_confirm(callback: types.CallbackQuery):
    await callback.answer()
    habit_id = int(callback.data.split("_")[1])
    habit = get_habit(habit_id)

    if not habit:
        await callback.message.edit_text("❌ Привычка не найдена.")
        return

    await callback.message.edit_text(
        f"🗑 <b>Удалить привычку?</b>\n\n"
        f"Вы уверены, что хотите удалить «{habit['name']}»?\n"
        f"Все данные о выполнении будут потеряны.",
        reply_markup=confirm_delete_keyboard(habit_id),
    )


@router.callback_query(F.data.startswith("confirm_delete_"))
async def confirm_delete(callback: types.CallbackQuery):
    await callback.answer()
    habit_id = int(callback.data.split("_")[2])
    delete_habit(habit_id)
    await callback.message.edit_text(
        "🗑 <b>Привычка удалена.</b>",
        reply_markup=main_menu_keyboard(),
    )


@router.callback_query(F.data.startswith("edit_"))
async def edit_habit_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    habit_id = int(callback.data.split("_")[1])
    habit = get_habit(habit_id)

    if not habit:
        await callback.message.edit_text("❌ Привычка не найдена.")
        return

    await state.update_data(habit_id=habit_id)
    await state.set_state(EditHabitForm.name)
    await callback.message.edit_text(
        f"✏️ <b>Редактирование</b>\n\n"
        f"Текущее название: <b>{habit['name']}</b>\n"
        f"Введите новое название (или отправьте «-», чтобы оставить текущее):",
        reply_markup=back_to_habit_keyboard(habit_id),
    )


@router.message(StateFilter(EditHabitForm.name))
async def edit_habit_name(message: types.Message, state: FSMContext):
    name = message.text.strip()
    data = await state.get_data()

    if name == "-":
        habit = get_habit(data["habit_id"])
        name = habit["name"] if habit else name

    if len(name) > 100:
        await message.answer("❌ Название слишком длинное. Попробуйте снова:")
        return

    await state.update_data(name=name)
    await state.set_state(EditHabitForm.description)
    await message.answer(
        f"✏️ Введите новое <b>описание</b> (или отправьте «-», чтобы оставить текущее):",
        reply_markup=back_to_habit_keyboard(data["habit_id"]),
    )


@router.message(StateFilter(EditHabitForm.description))
async def edit_habit_description(message: types.Message, state: FSMContext):
    desc = message.text.strip()
    data = await state.get_data()

    if desc == "-":
        habit = get_habit(data["habit_id"])
        desc = habit["description"] if habit else ""

    if len(desc) > 300:
        await message.answer("❌ Описание слишком длинное. Попробуйте снова:")
        return

    await state.update_data(description=desc)
    await state.set_state(EditHabitForm.frequency)
    await message.answer(
        f"📅 Выберите <b>периодичность</b>:",
        reply_markup=frequency_keyboard(),
    )


@router.callback_query(StateFilter(EditHabitForm.frequency), F.data.startswith("freq_"))
async def edit_habit_frequency(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    freq = callback.data.split("_")[1]
    data = await state.get_data()
    habit_id = data["habit_id"]

    update_habit(habit_id, data["name"], data["description"], freq)
    await state.clear()

    freq_text = "ежедневно" if freq == "daily" else "еженедельно"
    await callback.message.edit_text(
        f"✅ <b>Привычка обновлена!</b>\n\n"
        f"📌 {data['name']}\n"
        f"📅 {freq_text}\n"
        f"📝 {data.get('description', 'без описания')}",
        reply_markup=habit_actions_keyboard(habit_id, False),
    )
