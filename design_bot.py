import asyncio
import json
import os
import signal
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
ADMIN_IDS = [1031022066, 480615667, 1126310185]
PROJECT_NAME = "🏠 Будущий дом"
DATA_FILE = "user_forms.json"

# Защита от флуда
MESSAGE_DELAY = 0.5
CALLBACK_DELAY = 0.3
# ================================

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="Markdown"))
dp = Dispatcher()
user_forms = {}
waiting_for_design = {}
waiting_for_message = {}

async def safe_send(message_func, *args, **kwargs):
    await asyncio.sleep(MESSAGE_DELAY)
    return await message_func(*args, **kwargs)

def load_forms():
    global user_forms
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            user_forms = json.load(f)
    else:
        user_forms = {}

def save_forms():
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(user_forms, f, ensure_ascii=False, indent=2)

load_forms()

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

# ========== FSM ==========
class Form(StatesGroup):
    room = State()
    area = State()
    windows = State()
    style = State()
    mood = State()
    budget = State()
    colors_like = State()
    colors_dislike = State()
    light_dark = State()
    zones = State()
    people = State()
    lighting = State()
    furniture = State()
    appliances = State()
    eco = State()
    pets = State()
    dislike = State()
    like = State()
    confirm = State()
    photo = State()

class AdminStates(StatesGroup):
    waiting_user_id_photo = State()
    waiting_user_id_text = State()
    waiting_message_text = State()

def inline_buttons(options, prefix, cols=2):
    builder = InlineKeyboardBuilder()
    for opt in options:
        builder.button(text=opt, callback_data=f"{prefix}_{opt}")
    builder.adjust(cols)
    return builder.as_markup()

async def show_admin_menu(message: Message):
    if is_admin(message.from_user.id):
        await safe_send(message.answer, "👑 *Админ-панель*", parse_mode="Markdown", reply_markup=admin_menu)

# ========== СТАРТ ==========
@dp.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await state.clear()
    await safe_send(message.answer,
        f"{PROJECT_NAME}\n\n🌟 Добро пожаловать!\n\nНажми «Новый проект», чтобы начать опрос (20 вопросов).",
        reply_markup=main_menu
    )
    if is_admin(message.from_user.id):
        await show_admin_menu(message)

@dp.message(F.text == "🏠 Меню")
async def menu(message: Message, state: FSMContext):
    await state.clear()
    await safe_send(message.answer, "Главное меню", reply_markup=main_menu)
    if is_admin(message.from_user.id):
        await show_admin_menu(message)

@dp.message(F.text == "❌ Отмена")
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await safe_send(message.answer, "Опрос отменён", reply_markup=main_menu)
    if is_admin(message.from_user.id):
        await show_admin_menu(message)

@dp.message(F.text == "🔙 В главное меню")
async def back_main(message: Message, state: FSMContext):
    await state.clear()
    await safe_send(message.answer, "Главное меню", reply_markup=main_menu)
    if is_admin(message.from_user.id):
        await show_admin_menu(message)

# ========== АДМИН-ПАНЕЛЬ ==========
@dp.message(F.text == "📋 Список клиентов")
async def users_list(message: Message):
    if not is_admin(message.from_user.id):
        return
    if not user_forms:
        await safe_send(message.answer, "📭 *Нет заявок*", parse_mode="Markdown")
        return
    text = "📋 *Список клиентов:*\n\n"
    for uid, data in user_forms.items():
        text += f"🆔 `{uid}` — {data.get('name', '?')}\n   📅 {data.get('date', '?')}\n\n"
    if len(text) > 4000:
        text = text[:3500] + "\n\n..."
    await safe_send(message.answer, text, parse_mode="Markdown")

@dp.message(F.text == "📊 Статистика")
async def stats(message: Message):
    if not is_admin(message.from_user.id):
        return
    await safe_send(message.answer,
        f"📊 *Статистика*\n\n👥 Заявок: {len(user_forms)}\n👑 Админов: {len(ADMIN_IDS)}",
        parse_mode="Markdown"
    )

@dp.message(F.text == "✏️ Отправить дизайн")
async def send_design(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(AdminStates.waiting_user_id_photo)
    await safe_send(message.answer,
        "📸 *Введите ID пользователя* (число):\n\nID можно найти в списке клиентов",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🔙 Отмена")]], resize_keyboard=True)
    )

@dp.message(F.text == "💬 Отправить сообщение")
async def send_msg(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(AdminStates.waiting_user_id_text)
    await safe_send(message.answer,
        "💬 *Введите ID пользователя* (число):",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🔙 Отмена")]], resize_keyboard=True)
    )

@dp.message(AdminStates.waiting_user_id_photo)
async def get_id_photo(message: Message, state: FSMContext):
    if message.text == "🔙 Отмена":
        await state.clear()
        await safe_send(message.answer, "Отменено", reply_markup=admin_menu)
        return
    try:
        uid = int(message.text.strip())
        waiting_for_design[message.from_user.id] = uid
        await state.clear()
        await safe_send(message.answer,
            f"📸 *Отправьте фото дизайна* для пользователя `{uid}`",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🔙 Отмена")]], resize_keyboard=True)
        )
    except ValueError:
        await safe_send(message.answer, "❌ Введите число или нажмите «Отмена»")

@dp.message(AdminStates.waiting_user_id_text)
async def get_id_text(message: Message, state: FSMContext):
    if message.text == "🔙 Отмена":
        await state.clear()
        await safe_send(message.answer, "Отменено", reply_markup=admin_menu)
        return
    try:
        uid = int(message.text.strip())
        waiting_for_message[message.from_user.id] = uid
        await state.set_state(AdminStates.waiting_message_text)
        await safe_send(message.answer,
            f"💬 *Введите текст сообщения* для пользователя `{uid}`",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🔙 Отмена")]], resize_keyboard=True)
        )
    except ValueError:
        await safe_send(message.answer, "❌ Введите число или нажмите «Отмена»")

@dp.message(AdminStates.waiting_message_text)
async def send_text_message(message: Message, state: FSMContext):
    if message.text == "🔙 Отмена":
        await state.clear()
        await safe_send(message.answer, "Отменено", reply_markup=admin_menu)
        return
    uid = waiting_for_message.get(message.from_user.id)
    if not uid:
        await state.clear()
        await safe_send(message.answer, "Ошибка. Начните заново.", reply_markup=admin_menu)
        return
    try:
        await safe_send(bot.send_message,
            uid,
            f"✉️ *Сообщение от дизайнера:*\n\n{message.text}\n\n— {PROJECT_NAME}",
            parse_mode="Markdown"
        )
        await safe_send(message.answer, f"✅ *Сообщение отправлено* пользователю `{uid}`", parse_mode="Markdown")
        del waiting_for_message[message.from_user.id]
    except Exception as e:
        await safe_send(message.answer, f"❌ *Ошибка:* {e}", parse_mode="Markdown")
    await state.clear()
    await safe_send(message.answer, "Вернулись в админ-меню", reply_markup=admin_menu)

# ========== ОПРОС (20 ВОПРОСОВ) ==========
@dp.message(F.text == "🆕 Новый проект")
async def np(message: Message, state: FSMContext):
    await state.clear()
    await safe_send(message.answer, "📋 *Вопрос 1/20: Какую комнату хотите оформить?*", parse_mode="Markdown", reply_markup=nav_kb)
    await safe_send(message.answer, "Выберите:", reply_markup=inline_buttons(
        ["Гостиная", "Спальня", "Кухня", "Детская", "Ванная", "Кабинет", "Прихожая", "Балкон"], "room"))

@dp.callback_query(Form.room, F.data.startswith("room_"))
async def q1(call: CallbackQuery, state: FSMContext):
    await asyncio.sleep(CALLBACK_DELAY)
    await call.message.delete()
    await state.update_data(room=call.data.split("_")[1])
    await safe_send(call.message.answer, "📏 *Вопрос 2/20: Площадь комнаты?*", parse_mode="Markdown", reply_markup=nav_kb)
    await safe_send(call.message.answer, "Выберите:", reply_markup=inline_buttons(
        ["До 12 м²", "12-20 м²", "20+ м²", "Не знаю"], "area"))
    await state.set_state(Form.area)

@dp.callback_query(Form.area, F.data.startswith("area_"))
async def q2(call: CallbackQuery, state: FSMContext):
    await asyncio.sleep(CALLBACK_DELAY)
    await call.message.delete()
    await state.update_data(area=call.data.split("_")[1])
    await safe_send(call.message.answer, "🪟 *Вопрос 3/20: Сколько окон в комнате?*", parse_mode="Markdown", reply_markup=nav_kb)
    await safe_send(call.message.answer, "Выберите:", reply_markup=inline_buttons(
        ["Нет окон", "1 окно", "2 окна", "Больше 2"], "windows"))
    await state.set_state(Form.windows)

@dp.callback_query(Form.windows, F.data.startswith("windows_"))
async def q3(call: CallbackQuery, state: FSMContext):
    await asyncio.sleep(CALLBACK_DELAY)
    await call.message.delete()
    await state.update_data(windows=call.data.split("_")[1])
    await safe_send(call.message.answer, "🎨 *Вопрос 4/20: Какой стиль интерьера?*", parse_mode="Markdown", reply_markup=nav_kb)
    await safe_send(call.message.answer, "Выберите:", reply_markup=inline_buttons(
        ["Современный", "Минимализм", "Лофт", "Скандинавский", "Классика", "Прованс", "Эко", "Свой вариант"], "style"))
    await state.set_state(Form.style)

@dp.callback_query(Form.style, F.data == "style_Свой вариант")
async def custom_style(call: CallbackQuery, state: FSMContext):
    await asyncio.sleep(CALLBACK_DELAY)
    await call.message.delete()
    await safe_send(call.message.answer, "✏️ Напишите свой вариант стиля:", reply_markup=nav_kb)
    await state.set_state(Form.style)

@dp.callback_query(Form.style, F.data.startswith("style_"))
async def q4(call: CallbackQuery, state: FSMContext):
    await asyncio.sleep(CALLBACK_DELAY)
    await call.message.delete()
    await state.update_data(style=call.data.split("_")[1])
    await safe_send(call.message.answer, "🧘 *Вопрос 5/20: Какое настроение хотите создать?*", parse_mode="Markdown", reply_markup=nav_kb)
    await safe_send(call.message.answer, "Выберите:", reply_markup=inline_buttons(
        ["Уютное", "Строгое", "Романтичное", "Игривое", "Яркое", "Спокойное", "Минималистичное", "Другое"], "mood"))
    await state.set_state(Form.mood)

@dp.message(Form.style)
async def custom_style_text(msg: Message, state: FSMContext):
    await state.update_data(style=msg.text)
    await safe_send(msg.answer, "🧘 *Вопрос 5/20: Какое настроение хотите создать?*", parse_mode="Markdown", reply_markup=nav_kb)
    await safe_send(msg.answer, "Выберите:", reply_markup=inline_buttons(
        ["Уютное", "Строгое", "Романтичное", "Игривое", "Яркое", "Спокойное", "Минималистичное", "Другое"], "mood"))
    await state.set_state(Form.mood)

@dp.callback_query(Form.mood, F.data == "mood_Другое")
async def custom_mood(call: CallbackQuery, state: FSMContext):
    await asyncio.sleep(CALLBACK_DELAY)
    await call.message.delete()
    await safe_send(call.message.answer, "✏️ Опишите желаемое настроение:", reply_markup=nav_kb)
    await state.set_state(Form.mood)

@dp.callback_query(Form.mood, F.data.startswith("mood_"))
async def q5(call: CallbackQuery, state: FSMContext):
    await asyncio.sleep(CALLBACK_DELAY)
    await call.message.delete()
    await state.update_data(mood=call.data.split("_")[1])
    await safe_send(call.message.answer, "💰 *Вопрос 6/20: Какой бюджет на проект?*", parse_mode="Markdown", reply_markup=nav_kb)
    await safe_send(call.message.answer, "Выберите:", reply_markup=inline_buttons(
        ["Эконом", "Средний бюджет", "Премиум", "Без разницы"], "budget"))
    await state.set_state(Form.budget)

@dp.message(Form.mood)
async def custom_mood_text(msg: Message, state: FSMContext):
    await state.update_data(mood=msg.text)
    await safe_send(msg.answer, "💰 *Вопрос 6/20: Какой бюджет на проект?*", parse_mode="Markdown", reply_markup=nav_kb)
    await safe_send(msg.answer, "Выберите:", reply_markup=inline_buttons(
        ["Эконом", "Средний бюджет", "Премиум", "Без разницы"], "budget"))
    await state.set_state(Form.budget)

@dp.callback_query(Form.budget, F.data.startswith("budget_"))
async def q6(call: CallbackQuery, state: FSMContext):
    await asyncio.sleep(CALLBACK_DELAY)
    await call.message.delete()
    await state.update_data(budget=call.data.split("_")[1])
    await safe_send(call.message.answer, "🎨 *Вопрос 7/20: Какие цвета хотите видеть?* (через запятую)", parse_mode="Markdown", reply_markup=nav_kb)
    await state.set_state(Form.colors_like)

@dp.message(Form.colors_like)
async def q7(msg: Message, state: FSMContext):
    await state.update_data(colors_like=msg.text)
    await safe_send(msg.answer, "🚫 *Вопрос 8/20: Какие цвета НЕ хотите?* (напишите «нет»)", parse_mode="Markdown", reply_markup=nav_kb)
    await state.set_state(Form.colors_dislike)

@dp.message(Form.colors_dislike)
async def q8(msg: Message, state: FSMContext):
    val = "нет" if msg.text.lower() in ["нет", "пропустить"] else msg.text
    await state.update_data(colors_dislike=val)
    await safe_send(msg.answer, "☯️ *Вопрос 9/20: Светлые или тёмные тона?*", parse_mode="Markdown", reply_markup=nav_kb)
    await safe_send(msg.answer, "Выберите:", reply_markup=inline_buttons(["Светлые", "Тёмные", "Смешанные"], "lightdark"))
    await state.set_state(Form.light_dark)

@dp.callback_query(Form.light_dark, F.data.startswith("lightdark_"))
async def q9(call: CallbackQuery, state: FSMContext):
    await asyncio.sleep(CALLBACK_DELAY)
    await call.message.delete()
    await state.update_data(light_dark=call.data.split("_")[1])
    await safe_send(call.message.answer, "📌 *Вопрос 10/20: Какие зоны должны быть?* (выберите, затем «Готово»)", parse_mode="Markdown", reply_markup=nav_kb)
    await safe_send(call.message.answer, "Зоны:", reply_markup=inline_buttons(
        ["Отдых", "Работа", "Приём гостей", "Хранение", "Обеденная", "Спорт", "Другое"], "zone"))
    await state.update_data(zones=[])
    await state.set_state(Form.zones)

@dp.callback_query(Form.zones, F.data.startswith("zone_"))
async def zone_choice(call: CallbackQuery, state: FSMContext):
    zone = call.data.split("_")[1]
    data = await state.get_data()
    zones = data.get("zones", [])
    if zone == "Другое":
        await asyncio.sleep(CALLBACK_DELAY)
        await call.message.delete()
        await safe_send(call.message.answer, "✏️ Напишите название зоны:", reply_markup=nav_kb)
        await state.set_state(Form.zones)
        return
    if zone not in zones:
        zones.append(zone)
        await state.update_data(zones=zones)
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Готово", callback_data="zones_done")
    await call.message.edit_reply_markup(reply_markup=builder.as_markup())

@dp.callback_query(F.data == "zones_done")
async def zones_done(call: CallbackQuery, state: FSMContext):
    await asyncio.sleep(CALLBACK_DELAY)
    await call.message.delete()
    await safe_send(call.message.answer, "👥 *Вопрос 11/20: Сколько человек будут использовать комнату?*", parse_mode="Markdown", reply_markup=nav_kb)
    await safe_send(call.message.answer, "Выберите:", reply_markup=inline_buttons(["1", "2-3", "4+"], "people"))
    await state.set_state(Form.people)

@dp.message(Form.zones)
async def zone_other(msg: Message, state: FSMContext):
    data = await state.get_data()
    zones = data.get("zones", [])
    zones.append(msg.text)
    await state.update_data(zones=zones)
    await safe_send(msg.answer, "👥 *Вопрос 11/20: Сколько человек будут использовать комнату?*", parse_mode="Markdown", reply_markup=nav_kb)
    await safe_send(msg.answer, "Выберите:", reply_markup=inline_buttons(["1", "2-3", "4+"], "people"))
    await state.set_state(Form.people)

@dp.callback_query(Form.people, F.data.startswith("people_"))
async def q11(call: CallbackQuery, state: FSMContext):
    await asyncio.sleep(CALLBACK_DELAY)
    await call.message.delete()
    await state.update_data(people=call.data.split("_")[1])
    await safe_send(call.message.answer, "💡 *Вопрос 12/20: Какой тип освещения нравится?*", parse_mode="Markdown", reply_markup=nav_kb)
    await safe_send(call.message.answer, "Выберите:", reply_markup=inline_buttons(
        ["Естественное+доп.", "Только верхний", "Много точечных", "Мягкий рассеянный", "Яркое белое", "Тёплое жёлтое"], "lighting"))
    await state.set_state(Form.lighting)

@dp.callback_query(Form.lighting, F.data.startswith("lighting_"))
async def q12(call: CallbackQuery, state: FSMContext):
    await asyncio.sleep(CALLBACK_DELAY)
    await call.message.delete()
    await state.update_data(lighting=call.data.split("_")[1])
    await safe_send(call.message.answer, "🪑 *Вопрос 13/20: Какая мебель обязательно нужна?* (через запятую)", parse_mode="Markdown", reply_markup=nav_kb)
    await state.set_state(Form.furniture)

@dp.message(Form.furniture)
async def q13(msg: Message, state: FSMContext):
    await state.update_data(furniture=msg.text)
    await safe_send(msg.answer, "🔌 *Вопрос 14/20: Крупная техника?* (нет/перечислить)", parse_mode="Markdown", reply_markup=nav_kb)
    await state.set_state(Form.appliances)

@dp.message(Form.appliances)
async def q14(msg: Message, state: FSMContext):
    await state.update_data(appliances=msg.text)
    await safe_send(msg.answer, "🌿 *Вопрос 15/20: Экологичные материалы важны?*", parse_mode="Markdown", reply_markup=nav_kb)
    await safe_send(msg.answer, "Выберите:", reply_markup=inline_buttons(["Да", "Нет"], "eco"))
    await state.set_state(Form.eco)

@dp.callback_query(Form.eco, F.data.startswith("eco_"))
async def q15(call: CallbackQuery, state: FSMContext):
    await asyncio.sleep(CALLBACK_DELAY)
    await call.message.delete()
    await state.update_data(eco=call.data.split("_")[1])
    await safe_send(call.message.answer, "🐾 *Вопрос 16/20: Есть ли домашние питомцы?*", parse_mode="Markdown", reply_markup=nav_kb)
    await safe_send(call.message.answer, "Выберите:", reply_markup=inline_buttons(["Кошка", "Собака", "Грызуны", "Нет"], "pets"))
    await state.set_state(Form.pets)

@dp.callback_query(Form.pets, F.data.startswith("pets_"))
async def q16(call: CallbackQuery, state: FSMContext):
    await asyncio.sleep(CALLBACK_DELAY)
    await call.message.delete()
    await state.update_data(pets=call.data.split("_")[1])
    await safe_send(call.message.answer, "😞 *Вопрос 17/20: Что вам не нравится в текущем интерьере?*", parse_mode="Markdown", reply_markup=nav_kb)
    await state.set_state(Form.dislike)

@dp.message(Form.dislike)
async def q17(msg: Message, state: FSMContext):
    await state.update_data(dislike=msg.text)
    await safe_send(msg.answer, "❤️ *Вопрос 18/20: Что хотите сохранить из текущего?*", parse_mode="Markdown", reply_markup=nav_kb)
    await state.set_state(Form.like)

@dp.message(Form.like)
async def q18(msg: Message, state: FSMContext):
    await state.update_data(like=msg.text)
    data = await state.get_data()
    zones_txt = ", ".join(data.get("zones", []))
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
📌 Зоны: {zones_txt}
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
    await safe_send(msg.answer, preview, parse_mode="Markdown", reply_markup=nav_kb)
    await safe_send(msg.answer, "Всё верно?", reply_markup=inline_buttons(["✅ Да, всё верно", "🔄 Начать заново"], "confirm"))
    await state.set_state(Form.confirm)

# ========== ФОТО ==========
@dp.callback_query(Form.confirm, F.data == "confirm_✅ Да, всё верно")
async def confirm_yes(call: CallbackQuery, state: FSMContext):
    await asyncio.sleep(CALLBACK_DELAY)
    await call.message.delete()
    await safe_send(call.message.answer,
        "📸 *Вопрос 20/20: Пришлите 1-3 фото комнаты*\n\n"
        "Отправляйте фото по одному. Когда загрузите все, нажмите кнопку «✅ Готово».",
        parse_mode="Markdown",
        reply_markup=nav_kb
    )
    await state.update_data(photos=[])
    await state.set_state(Form.photo)
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Готово", callback_data="photos_done")
    await safe_send(call.message.answer, "👇 Кнопка для завершения:", reply_markup=builder.as_markup())

@dp.callback_query(Form.confirm, F.data == "confirm_🔄 Начать заново")
async def confirm_no(call: CallbackQuery, state: FSMContext):
    await asyncio.sleep(CALLBACK_DELAY)
    await call.message.delete()
    await np(call.message, state)

@dp.message(Form.photo, F.photo)
async def add_photo(msg: Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])
    
    if len(photos) >= 3:
        await safe_send(msg.answer, "❌ Вы уже отправили 3 фото. Нажмите «Готово».")
        return
    
    photos.append(msg.photo[-1].file_id)
    await state.update_data(photos=photos)
    
    remaining = 3 - len(photos)
    await safe_send(msg.answer, f"📸 Фото {len(photos)}/3 сохранено. Осталось {remaining}.")
    
    if len(photos) == 3:
        await safe_send(msg.answer, "✅ Вы отправили 3 фото. Заявка отправляется...")
        await finish_survey(msg, state)

@dp.callback_query(F.data == "photos_done")
async def photos_done_callback(call: CallbackQuery, state: FSMContext):
    await asyncio.sleep(CALLBACK_DELAY)
    await call.message.delete()
    await finish_survey(call.message, state)

async def finish_survey(msg: Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])
    
    if not photos:
        await safe_send(msg.answer, "❌ Вы не отправили ни одного фото. Отправьте хотя бы 1 фото.")
        return

    user_forms[str(msg.from_user.id)] = {
        "user_id": msg.from_user.id,
        "name": msg.from_user.full_name,
        "username": msg.from_user.username,
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
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    save_forms()

    zones_txt = ", ".join(data.get("zones", []))
    caption = f"""
📋 *НОВАЯ ЗАЯВКА* #{datetime.now().strftime('%Y%m%d%H%M%S')}

🏠 {data.get('room')} | {data.get('area')} | {data.get('windows')}
🎨 {data.get('style')} | {data.get('mood')} | {data.get('budget')}
🎨 Цвета: {data.get('colors_like')}
🚫 Не надо: {data.get('colors_dislike')}
☯️ {data.get('light_dark')}
📌 Зоны: {zones_txt}
👥 {data.get('people')} чел.
💡 {data.get('lighting')}
🪑 {data.get('furniture')}
🔌 {data.get('appliances')}
🌿 {data.get('eco')}
🐾 {data.get('pets')}
😞 {data.get('dislike')}
❤️ {data.get('like')}

👤 {msg.from_user.full_name}
🆔 `{msg.from_user.id}`

📌 *Чтобы отправить дизайн:* используйте админ-меню → «Отправить дизайн»
"""
    for admin_id in ADMIN_IDS:
        try:
            await safe_send(bot.send_photo, admin_id, photos[0], caption=caption, parse_mode="Markdown")
            for p in photos[1:]:
                await safe_send(bot.send_photo, admin_id, p)
        except Exception as e:
            print(f"Ошибка админу {admin_id}: {e}")

    await safe_send(msg.answer,
        "✨ *ГОТОВО!* ✨\n\n"
        f"✅ Получено {len(photos)} фото\n\n"
        "Ваша заявка отправлена дизайнерам.\n\n"
        "Спасибо, что выбрали «Будущий дом»! 🏠",
        parse_mode="Markdown",
        reply_markup=main_menu
    )
    if is_admin(msg.from_user.id):
        await show_admin_menu(msg)
    await state.clear()

@dp.message(Form.photo)
async def wrong_photo_input(msg: Message):
    await safe_send(msg.answer, "❌ Отправьте фото комнаты в формате изображения.")

# ========== АДМИН: ОТПРАВКА ДИЗАЙНА ==========
@dp.message(F.photo)
async def admin_send_design_photo(message: Message):
    if not is_admin(message.from_user.id):
        return
    if message.from_user.id not in waiting_for_design:
        return
    
    user_id = waiting_for_design[message.from_user.id]
    photo_id = message.photo[-1].file_id
    
    try:
        await safe_send(bot.send_photo,
            user_id,
            photo_id,
            caption="🎉 *Ваш дизайн-проект готов!*\n\nСпасибо, что выбрали «Будущий дом»! 🏠",
            parse_mode="Markdown"
        )
        await safe_send(message.answer, f"✅ *Дизайн успешно отправлен* пользователю `{user_id}`", parse_mode="Markdown")
        del waiting_for_design[message.from_user.id]
    except Exception as e:
        await safe_send(message.answer, f"❌ *Ошибка отправки:* {str(e)}", parse_mode="Markdown")

# ========== ОБРАБОТКА SIGTERM ==========
async def shutdown():
    print("⚠️ Получен сигнал SIGTERM, бот завершает работу...")
    await bot.session.close()
    print("✅ Бот корректно остановлен")
    os._exit(0)

def handle_sigterm():
    asyncio.create_task(shutdown())

signal.signal(signal.SIGTERM, lambda s, f: handle_sigterm())

# ========== ЗАПУСК ==========
async def main():
    print(f"🤖 {PROJECT_NAME} запущен!")
    print(f"👑 Админы: {ADMIN_IDS}")
    print(f"📂 Загружено заявок: {len(user_forms)}")
    print(f"🌊 Защита от флуда: задержка {MESSAGE_DELAY}с между сообщениями")
    
    # Пытаемся остановить предыдущие экземпляры
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        print("🔄 Webhook очищен, старые обновления отброшены")
    except Exception as e:
        print(f"⚠️ Ошибка очистки webhook: {e}")
    
    await dp.start_polling(bot, polling_timeout=60)

if __name__ == "__main__":
    asyncio.run(main())
