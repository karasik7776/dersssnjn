import asyncio
import json
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties

# ========== НАСТРОЙКИ ==========
BOT_TOKEN = "8789237062:AAE03_Lw4-HO9cmxVn44-b4XHASCV-4Li50"
ADMIN_IDS = [1031022066, 480615667, 1126310185]          # можешь добавить ещё через запятую
PROJECT_NAME = "🏠 Будущий дом"
DATA_FILE = "user_forms.json"
# ================================

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="Markdown"))
dp = Dispatcher()

# ========== ХРАНИЛИЩЕ ==========
def load_forms():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_forms():
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(user_forms, f, ensure_ascii=False, indent=2)

user_forms = load_forms()
waiting_for_design = {}   # {admin_id: target_user_id}
waiting_for_message = {}  # {admin_id: target_user_id} (текст)

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

# ========== КЛАВИАТУРЫ ==========
main_menu = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🆕 Новый проект")]],
    resize_keyboard=True
)

admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📋 Список клиентов"), KeyboardButton(text="📊 Статистика")],
        [KeyboardButton(text="✏️ Отправить дизайн"), KeyboardButton(text="💬 Отправить сообщение")],
        [KeyboardButton(text="🔙 В главное меню")]
    ],
    resize_keyboard=True
)

nav_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="❌ Отмена"), KeyboardButton(text="🏠 Меню")]],
    resize_keyboard=True
)

# ========== FSM (полные 20 вопросов) ==========
class Form(StatesGroup):
    q_room = State()
    q_area = State()
    q_windows = State()
    q_style = State()
    q_mood = State()
    q_budget = State()
    q_colors_like = State()
    q_colors_dislike = State()
    q_light_dark = State()
    q_zones = State()
    q_people = State()
    q_lighting = State()
    q_furniture = State()
    q_appliances = State()
    q_eco = State()
    q_pets = State()
    q_dislike = State()
    q_like = State()
    q_confirm = State()
    q_photo = State()

class AdminStates(StatesGroup):
    waiting_for_user_id_photo = State()
    waiting_for_user_id_text = State()
    waiting_for_text_message = State()

def inline_buttons(options, prefix, cols=2):
    builder = InlineKeyboardBuilder()
    for opt in options:
        builder.button(text=opt, callback_data=f"{prefix}_{opt}")
    builder.adjust(cols)
    return builder.as_markup()

async def show_admin_menu(message: Message):
    if is_admin(message.from_user.id):
        await message.answer("👑 *Админ-панель*", parse_mode="Markdown", reply_markup=admin_menu)

# ========== СТАРТ И ОБЩИЕ КОМАНДЫ ==========
@dp.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"{PROJECT_NAME}\n\n🌟 Добро пожаловать!\n\nНажми «Новый проект», чтобы начать опрос (20 вопросов).",
        reply_markup=main_menu
    )
    if is_admin(message.from_user.id):
        await show_admin_menu(message)

@dp.message(F.text == "🏠 Меню")
async def menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Главное меню", reply_markup=main_menu)
    if is_admin(message.from_user.id):
        await show_admin_menu(message)

@dp.message(F.text == "❌ Отмена")
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Опрос отменён", reply_markup=main_menu)
    if is_admin(message.from_user.id):
        await show_admin_menu(message)

@dp.message(F.text == "🔙 В главное меню")
async def back_to_main(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Главное меню", reply_markup=main_menu)
    if is_admin(message.from_user.id):
        await show_admin_menu(message)

# ========== АДМИН-МЕНЮ (КНОПКИ) ==========
@dp.message(F.text == "📋 Список клиентов")
async def admin_users(message: Message):
    if not is_admin(message.from_user.id):
        return
    if not user_forms:
        await message.answer("📭 *Нет заявок*", parse_mode="Markdown")
        return
    text = "📋 *Список клиентов:*\n\n"
    for uid, data in user_forms.items():
        text += f"🆔 `{uid}` — {data.get('name', '?')}\n   📅 {data.get('date', '?')}\n\n"
    if len(text) > 4000:
        text = text[:3500] + "\n\n..."
    await message.answer(text, parse_mode="Markdown")

@dp.message(F.text == "📊 Статистика")
async def admin_stats(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer(
        f"📊 *Статистика*\n\n👥 Заявок: {len(user_forms)}\n👑 Админов: {len(ADMIN_IDS)}",
        parse_mode="Markdown"
    )

@dp.message(F.text == "✏️ Отправить дизайн")
async def admin_send_design(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(AdminStates.waiting_for_user_id_photo)
    await message.answer(
        "📸 *Введите ID пользователя* (из списка клиентов или от @userinfobot):",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="🔙 Отмена")]], resize_keyboard=True
        )
    )

@dp.message(F.text == "💬 Отправить сообщение")
async def admin_send_text(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(AdminStates.waiting_for_user_id_text)
    await message.answer(
        "💬 *Введите ID пользователя* (из списка клиентов):",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="🔙 Отмена")]], resize_keyboard=True
        )
    )

@dp.message(AdminStates.waiting_for_user_id_photo)
async def get_user_id_photo(message: Message, state: FSMContext):
    if message.text == "🔙 Отмена":
        await state.clear()
        await message.answer("Отменено", reply_markup=admin_menu)
        return
    try:
        user_id = int(message.text.strip())
        waiting_for_design[message.from_user.id] = user_id
        await state.clear()
        await message.answer(
            f"📸 *Отправьте фото дизайна* для пользователя `{user_id}`",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="🔙 Отмена")]], resize_keyboard=True
            )
        )
    except ValueError:
        await message.answer("❌ Неверный ID. Введите число.")

@dp.message(AdminStates.waiting_for_user_id_text)
async def get_user_id_text(message: Message, state: FSMContext):
    if message.text == "🔙 Отмена":
        await state.clear()
        await message.answer("Отменено", reply_markup=admin_menu)
        return
    try:
        user_id = int(message.text.strip())
        waiting_for_message[message.from_user.id] = user_id
        await state.set_state(AdminStates.waiting_for_text_message)
        await message.answer(
            f"💬 *Введите текст сообщения* для пользователя `{user_id}`",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="🔙 Отмена")]], resize_keyboard=True
            )
        )
    except ValueError:
        await message.answer("❌ Неверный ID. Введите число.")

@dp.message(AdminStates.waiting_for_text_message)
async def send_text_to_user(message: Message, state: FSMContext):
    if message.text == "🔙 Отмена":
        await state.clear()
        await message.answer("Отменено", reply_markup=admin_menu)
        return
    user_id = waiting_for_message.get(message.from_user.id)
    if not user_id:
        await state.clear()
        await message.answer("Ошибка: пользователь не найден", reply_markup=admin_menu)
        return
    try:
        await bot.send_message(
            user_id,
            f"✉️ *Сообщение от дизайнера:*\n\n{message.text}\n\n— {PROJECT_NAME}",
            parse_mode="Markdown"
        )
        await message.answer(f"✅ *Сообщение отправлено* пользователю `{user_id}`", parse_mode="Markdown")
    except Exception as e:
        await message.answer(f"❌ *Ошибка:* {e}", parse_mode="Markdown")
    del waiting_for_message[message.from_user.id]
    await state.clear()
    await message.answer("Вернулись в админ-меню", reply_markup=admin_menu)

@dp.message(F.photo)
async def forward_design_photo(message: Message):
    if not is_admin(message.from_user.id):
        return
    user_id = waiting_for_design.get(message.from_user.id)
    if not user_id:
        return
    try:
        await bot.send_photo(
            user_id,
            message.photo[-1].file_id,
            caption="🎉 *Ваш дизайн-проект готов!*\n\nСпасибо, что выбрали «Будущий дом»! 🏠",
            parse_mode="Markdown"
        )
        await message.answer(f"✅ *Дизайн отправлен* пользователю `{user_id}`", parse_mode="Markdown")
    except Exception as e:
        await message.answer(f"❌ *Ошибка:* {e}", parse_mode="Markdown")
    del waiting_for_design[message.from_user.id]

@dp.message(F.text == "🔙 Отмена")
async def cancel_action(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Действие отменено", reply_markup=admin_menu)

# ========== 20 ВОПРОСОВ (ПОЛНАЯ ЛОГИКА) ==========
@dp.message(F.text == "🆕 Новый проект")
async def new_project(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("📋 *Вопрос 1/20: Какую комнату хотите оформить?*", parse_mode="Markdown", reply_markup=nav_kb)
    await message.answer("Выберите:", reply_markup=inline_buttons(
        ["Гостиная", "Спальня", "Кухня", "Детская", "Ванная", "Кабинет", "Прихожая", "Балкон"], "room", 2))
    await state.set_state(Form.q_room)

@dp.callback_query(Form.q_room, F.data.startswith("room_"))
async def q1(call: CallbackQuery, state: FSMContext):
    await state.update_data(room=call.data.split("_")[1])
    await call.message.delete()
    await call.message.answer("📏 *Вопрос 2/20: Площадь комнаты?*", parse_mode="Markdown", reply_markup=nav_kb)
    await call.message.answer("Выберите:", reply_markup=inline_buttons(["До 12 м²", "12-20 м²", "20+ м²", "Не знаю"], "area", 2))
    await state.set_state(Form.q_area)
    await call.answer()

@dp.callback_query(Form.q_area, F.data.startswith("area_"))
async def q2(call: CallbackQuery, state: FSMContext):
    await state.update_data(area=call.data.split("_")[1])
    await call.message.delete()
    await call.message.answer("🪟 *Вопрос 3/20: Сколько окон?*", parse_mode="Markdown", reply_markup=nav_kb)
    await call.message.answer("Выберите:", reply_markup=inline_buttons(["Нет окон", "1 окно", "2 окна", "Больше 2"], "windows", 2))
    await state.set_state(Form.q_windows)
    await call.answer()

@dp.callback_query(Form.q_windows, F.data.startswith("windows_"))
async def q3(call: CallbackQuery, state: FSMContext):
    await state.update_data(windows=call.data.split("_")[1])
    await call.message.delete()
    await call.message.answer("🎨 *Вопрос 4/20: Какой стиль интерьера?*", parse_mode="Markdown", reply_markup=nav_kb)
    await call.message.answer("Выберите:", reply_markup=inline_buttons(
        ["Современный", "Минимализм", "Лофт", "Скандинавский", "Классика", "Прованс", "Бохо", "Эко", "Свой вариант"], "style", 2))
    await state.set_state(Form.q_style)
    await call.answer()

@dp.callback_query(Form.q_style, F.data == "style_Свой вариант")
async def custom_style(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer("✏️ Напишите ваш вариант стиля:", reply_markup=nav_kb)
    await state.set_state(Form.q_style)
    await call.answer()

@dp.callback_query(Form.q_style, F.data.startswith("style_"))
async def q4_style_chosen(call: CallbackQuery, state: FSMContext):
    await state.update_data(style=call.data.split("_")[1])
    await call.message.delete()
    await call.message.answer("🧘 *Вопрос 5/20: Какое настроение создать?*", parse_mode="Markdown", reply_markup=nav_kb)
    await call.message.answer("Выберите:", reply_markup=inline_buttons(
        ["Уютное", "Строгое", "Романтичное", "Игривое", "Яркое", "Спокойное", "Минималистичное", "Другое"], "mood", 2))
    await state.set_state(Form.q_mood)
    await call.answer()

@dp.message(Form.q_style)
async def custom_style_text(msg: Message, state: FSMContext):
    await state.update_data(style=msg.text)
    await msg.answer("🧘 *Вопрос 5/20: Какое настроение создать?*", parse_mode="Markdown", reply_markup=nav_kb)
    await msg.answer("Выберите:", reply_markup=inline_buttons(
        ["Уютное", "Строгое", "Романтичное", "Игривое", "Яркое", "Спокойное", "Минималистичное", "Другое"], "mood", 2))
    await state.set_state(Form.q_mood)

@dp.callback_query(Form.q_mood, F.data == "mood_Другое")
async def custom_mood(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer("✏️ Опишите желаемое настроение:", reply_markup=nav_kb)
    await state.set_state(Form.q_mood)
    await call.answer()

@dp.callback_query(Form.q_mood, F.data.startswith("mood_"))
async def q5_mood_chosen(call: CallbackQuery, state: FSMContext):
    await state.update_data(mood=call.data.split("_")[1])
    await call.message.delete()
    await call.message.answer("💰 *Вопрос 6/20: Бюджет?*", parse_mode="Markdown", reply_markup=nav_kb)
    await call.message.answer("Выберите:", reply_markup=inline_buttons(["Эконом", "Средний", "Премиум", "Без разницы"], "budget", 2))
    await state.set_state(Form.q_budget)
    await call.answer()

@dp.message(Form.q_mood)
async def custom_mood_text(msg: Message, state: FSMContext):
    await state.update_data(mood=msg.text)
    await msg.answer("💰 *Вопрос 6/20: Бюджет?*", parse_mode="Markdown", reply_markup=nav_kb)
    await msg.answer("Выберите:", reply_markup=inline_buttons(["Эконом", "Средний", "Премиум", "Без разницы"], "budget", 2))
    await state.set_state(Form.q_budget)

@dp.callback_query(Form.q_budget, F.data.startswith("budget_"))
async def q6_budget_chosen(call: CallbackQuery, state: FSMContext):
    await state.update_data(budget=call.data.split("_")[1])
    await call.message.delete()
    await call.message.answer("🎨 *Вопрос 7/20: Желаемые цвета?* (через запятую)", parse_mode="Markdown", reply_markup=nav_kb)
    await state.set_state(Form.q_colors_like)
    await call.answer()

@dp.message(Form.q_colors_like)
async def q7_colors_like(msg: Message, state: FSMContext):
    await state.update_data(colors_like=msg.text)
    await msg.answer("🚫 *Вопрос 8/20: Нежелаемые цвета?* (напишите «нет»)", parse_mode="Markdown", reply_markup=nav_kb)
    await state.set_state(Form.q_colors_dislike)

@dp.message(Form.q_colors_dislike)
async def q8_colors_dislike(msg: Message, state: FSMContext):
    val = "нет" if msg.text.lower() in ["нет", "пропустить"] else msg.text
    await state.update_data(colors_dislike=val)
    await msg.answer("☯️ *Вопрос 9/20: Светлые или тёмные тона?*", parse_mode="Markdown", reply_markup=nav_kb)
    await msg.answer("Выберите:", reply_markup=inline_buttons(["Светлые", "Тёмные", "Смешанные"], "lightdark", 2))
    await state.set_state(Form.q_light_dark)

@dp.callback_query(Form.q_light_dark, F.data.startswith("lightdark_"))
async def q9_light_dark(call: CallbackQuery, state: FSMContext):
    await state.update_data(light_dark=call.data.split("_")[1])
    await call.message.delete()
    await call.message.answer("📌 *Вопрос 10/20: Какие зоны нужны?* (выберите несколько, затем «Готово»)", parse_mode="Markdown", reply_markup=nav_kb)
    await call.message.answer("Зоны:", reply_markup=inline_buttons(
        ["Отдых", "Работа", "Приём гостей", "Хранение", "Обеденная", "Спорт", "Другое"], "zone", 2))
    await state.update_data(zones=[])
    await state.set_state(Form.q_zones)
    await call.answer()

@dp.callback_query(Form.q_zones, F.data.startswith("zone_"))
async def zone_choose(call: CallbackQuery, state: FSMContext):
    zone = call.data.split("_")[1]
    data = await state.get_data()
    zones = data.get("zones", [])
    if zone == "Другое":
        await call.message.delete()
        await call.message.answer("✏️ Напишите зону:", reply_markup=nav_kb)
        await state.set_state(Form.q_zones)
        await call.answer()
        return
    if zone not in zones:
        zones.append(zone)
        await state.update_data(zones=zones)
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Готово", callback_data="zones_done")
    await call.message.edit_reply_markup(reply_markup=builder.as_markup())
    await call.answer()

@dp.callback_query(F.data == "zones_done")
async def zones_done(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer("👥 *Вопрос 11/20: Сколько человек?*", parse_mode="Markdown", reply_markup=nav_kb)
    await call.message.answer("Выберите:", reply_markup=inline_buttons(["1", "2-3", "4+"], "people", 2))
    await state.set_state(Form.q_people)
    await call.answer()

@dp.message(Form.q_zones)
async def zone_other_text(msg: Message, state: FSMContext):
    data = await state.get_data()
    zones = data.get("zones", [])
    zones.append(msg.text)
    await state.update_data(zones=zones)
    await msg.answer("👥 *Вопрос 11/20: Сколько человек?*", parse_mode="Markdown", reply_markup=nav_kb)
    await msg.answer("Выберите:", reply_markup=inline_buttons(["1", "2-3", "4+"], "people", 2))
    await state.set_state(Form.q_people)

@dp.callback_query(Form.q_people, F.data.startswith("people_"))
async def q11_people(call: CallbackQuery, state: FSMContext):
    await state.update_data(people=call.data.split("_")[1])
    await call.message.delete()
    await call.message.answer("💡 *Вопрос 12/20: Освещение?*", parse_mode="Markdown", reply_markup=nav_kb)
    await call.message.answer("Выберите:", reply_markup=inline_buttons(
        ["Естественное+доп.", "Только верхний", "Много точечных", "Мягкий рассеянный", "Яркое белое", "Тёплое жёлтое"], "lighting", 2))
    await state.set_state(Form.q_lighting)
    await call.answer()

@dp.callback_query(Form.q_lighting, F.data.startswith("lighting_"))
async def q12_lighting(call: CallbackQuery, state: FSMContext):
    await state.update_data(lighting=call.data.split("_")[1])
    await call.message.delete()
    await call.message.answer("🪑 *Вопрос 13/20: Обязательная мебель?* (через запятую)", parse_mode="Markdown", reply_markup=nav_kb)
    await state.set_state(Form.q_furniture)
    await call.answer()

@dp.message(Form.q_furniture)
async def q13_furniture(msg: Message, state: FSMContext):
    await state.update_data(furniture=msg.text)
    await msg.answer("🔌 *Вопрос 14/20: Крупная техника?* (нет/перечислить)", parse_mode="Markdown", reply_markup=nav_kb)
    await state.set_state(Form.q_appliances)

@dp.message(Form.q_appliances)
async def q14_appliances(msg: Message, state: FSMContext):
    await state.update_data(appliances=msg.text)
    await msg.answer("🌿 *Вопрос 15/20: Эко-материалы важны?*", parse_mode="Markdown", reply_markup=nav_kb)
    await msg.answer("Выберите:", reply_markup=inline_buttons(["Да, важны", "Нет, не принципиально"], "eco", 2))
    await state.set_state(Form.q_eco)

@dp.callback_query(Form.q_eco, F.data.startswith("eco_"))
async def q15_eco(call: CallbackQuery, state: FSMContext):
    await state.update_data(eco=call.data.split("_")[1])
    await call.message.delete()
    await call.message.answer("🐾 *Вопрос 16/20: Питомцы?*", parse_mode="Markdown", reply_markup=nav_kb)
    await call.message.answer("Выберите:", reply_markup=inline_buttons(["Кошка", "Собака", "Грызуны", "Нет"], "pets", 2))
    await state.set_state(Form.q_pets)
    await call.answer()

@dp.callback_query(Form.q_pets, F.data.startswith("pets_"))
async def q16_pets(call: CallbackQuery, state: FSMContext):
    await state.update_data(pets=call.data.split("_")[1])
    await call.message.delete()
    await call.message.answer("😞 *Вопрос 17/20: Что не нравится в интерьере?*", parse_mode="Markdown", reply_markup=nav_kb)
    await state.set_state(Form.q_dislike)
    await call.answer()

@dp.message(Form.q_dislike)
async def q17_dislike(msg: Message, state: FSMContext):
    await state.update_data(dislike=msg.text)
    await msg.answer("❤️ *Вопрос 18/20: Что сохранить из текущего?*", parse_mode="Markdown", reply_markup=nav_kb)
    await state.set_state(Form.q_like)

@dp.message(Form.q_like)
async def q18_like(msg: Message, state: FSMContext):
    await state.update_data(like=msg.text)
    data = await state.get_data()
    zones_text = ", ".join(data.get("zones", []))
    preview = f"""
📋 *ПРОВЕРЬТЕ ОТВЕТЫ*

🏠 Комната: {data.get('room')}
📏 Площадь: {data.get('area')}
🪟 Окна: {data.get('windows')}
🎨 Стиль: {data.get('style')}
🧘 Настроение: {data.get('mood')}
💰 Бюджет: {data.get('budget')}
🎨 Желаемые цвета: {data.get('colors_like')}
🚫 Нежелаемые: {data.get('colors_dislike')}
☯️ Тона: {data.get('light_dark')}
📌 Зоны: {zones_text}
👥 Количество человек: {data.get('people')}
💡 Освещение: {data.get('lighting')}
🪑 Мебель: {data.get('furniture')}
🔌 Техника: {data.get('appliances')}
🌿 Эко: {data.get('eco')}
🐾 Питомцы: {data.get('pets')}
😞 Не нравится: {data.get('dislike')}
❤️ Сохранить: {data.get('like')}

✅ *Вопрос 19/20: Всё верно?*
"""
    await msg.answer(preview, parse_mode="Markdown", reply_markup=nav_kb)
    await msg.answer("Всё верно?", reply_markup=inline_buttons(["✅ Да, всё верно", "🔄 Начать заново"], "confirm", 2))
    await state.set_state(Form.q_confirm)

@dp.callback_query(Form.q_confirm, F.data == "confirm_✅ Да, всё верно")
async def confirm_yes(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer(
        "📸 *Вопрос 20/20: Пришлите 1–3 фото комнаты*\n\nОтправляйте фото по одному. Когда закончите – нажмите «✅ Готово, отправить»",
        parse_mode="Markdown", reply_markup=nav_kb
    )
    await state.update_data(photos=[])
    await state.set_state(Form.q_photo)
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Готово, отправить", callback_data="photos_done")
    await call.message.answer("👇 После всех фото нажмите кнопку:", reply_markup=builder.as_markup())
    await call.answer()

@dp.callback_query(Form.q_confirm, F.data == "confirm_🔄 Начать заново")
async def confirm_no(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await new_project(call.message, state)
    await call.answer()

@dp.message(Form.q_photo, F.photo)
async def get_photo(msg: Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])
    if len(photos) >= 3:
        await msg.answer("❌ Вы отправили уже 3 фото. Нажмите «Готово».")
        return
    photos.append(msg.photo[-1].file_id)
    await state.update_data(photos=photos)
    await msg.answer(f"📸 Фото {len(photos)}/3 сохранено. Отправьте ещё или нажмите «Готово».")

@dp.callback_query(F.data == "photos_done")
async def photos_done(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])
    if not photos:
        await call.message.answer("❌ Отправьте хотя бы одно фото.")
        return

    user_forms[str(call.from_user.id)] = {
        "user_id": call.from_user.id,
        "name": call.from_user.full_name,
        "username": call.from_user.username,
        "room": data.get("room"),
        "area": data.get("area"),
        "windows": data.get("windows"),
        "style": data.get("style"),
        "mood": data.get("mood"),
        "budget": data.get("budget"),
        "colors_like": data.get("colors_like"),
        "colors_dislike": data.get("colors_dislike"),
        "light_dark": data.get("light_dark"),
        "zones": ", ".join(data.get("zones", [])),
        "people": data.get("people"),
        "lighting": data.get("lighting"),
        "furniture": data.get("furniture"),
        "appliances": data.get("appliances"),
        "eco": data.get("eco"),
        "pets": data.get("pets"),
        "dislike": data.get("dislike"),
        "like": data.get("like"),
        "photo_id": photos[0],
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    save_forms()

    caption = f"""
📋 *НОВАЯ ЗАЯВКА* #{datetime.now().strftime('%Y%m%d%H%M%S')}

🏠 {data.get('room')} | {data.get('area')} | {data.get('windows')}
🎨 {data.get('style')} | {data.get('mood')} | {data.get('budget')}
🎨 Цвета: {data.get('colors_like')}
🚫 Не надо: {data.get('colors_dislike')}
☯️ {data.get('light_dark')}
📌 Зоны: {', '.join(data.get('zones', []))}
👥 {data.get('people')} чел.
💡 {data.get('lighting')}
🪑 {data.get('furniture')}
🔌 {data.get('appliances')}
🌿 {data.get('eco')}
🐾 {data.get('pets')}
😞 {data.get('dislike')}
❤️ {data.get('like')}

👤 {call.from_user.full_name}
🆔 `{call.from_user.id}`
"""
    for admin_id in ADMIN_IDS:
        await bot.send_photo(admin_id, photos[0], caption=caption, parse_mode="Markdown")
        for i in range(1, len(photos)):
            await bot.send_photo(admin_id, photos[i])
    await call.message.edit_text("✨ *ГОТОВО!* Заявка отправлена дизайнерам.", parse_mode="Markdown", reply_markup=main_menu)
    if is_admin(call.from_user.id):
        await show_admin_menu(call.message)
    await state.clear()
    await call.answer()

@dp.message(Form.q_photo)
async def wrong_photo_input(msg: Message):
    await msg.answer("❌ Отправьте фото комнаты.")

# ========== ЗАПУСК ==========
async def main():
    print(f"🤖 {PROJECT_NAME} запущен (20 вопросов, админ-меню, сохранение в json)")
    print(f"👑 Админы: {ADMIN_IDS}")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
