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
ADMIN_IDS = [1031022066]
PROJECT_NAME = "🏠 Будущий дом"
DATA_FILE = "user_forms.json"
# ================================

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="Markdown"))
dp = Dispatcher()

# Загрузка заявок из файла
def load_forms():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_forms():
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(user_forms, f, ensure_ascii=False, indent=2)

user_forms = load_forms()
waiting_for_design = {}

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

# ========== СОСТОЯНИЯ ==========
class Form(StatesGroup):
    waiting_for_room = State()
    waiting_for_area = State()
    waiting_for_windows = State()
    waiting_for_style = State()
    waiting_for_mood = State()
    waiting_for_budget = State()
    waiting_for_colors = State()
    waiting_for_photo = State()

class AdminStates(StatesGroup):
    waiting_for_user_id = State()
    waiting_for_design_photo = State()
    waiting_for_message_text = State()

def inline_buttons(options, prefix, cols=2):
    builder = InlineKeyboardBuilder()
    for opt in options:
        builder.button(text=opt, callback_data=f"{prefix}_{opt}")
    builder.adjust(cols)
    return builder.as_markup()

async def show_admin_menu(message: Message):
    if is_admin(message.from_user.id):
        await message.answer("👑 *Админ-панель*", parse_mode="Markdown", reply_markup=admin_menu)

# ========== КОМАНДЫ ==========
@dp.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"{PROJECT_NAME}\n\n🌟 Добро пожаловать!\n\nНажми «Новый проект», чтобы начать.",
        reply_markup=main_menu
    )
    if is_admin(message.from_user.id):
        await show_admin_menu(message)

@dp.message(F.text == "🔙 В главное меню")
async def back_to_main(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Главное меню", reply_markup=main_menu)
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

# ========== АДМИН-МЕНЮ ==========
@dp.message(F.text == "📋 Список клиентов")
async def admin_users(message: Message):
    if not is_admin(message.from_user.id):
        return
    
    if not user_forms:
        await message.answer("📭 *Нет заявок*", parse_mode="Markdown")
        return
    
    text = "📋 *Список клиентов:*\n\n"
    for uid, data in user_forms.items():
        text += f"🆔 `{uid}` - {data.get('name', '?')}\n"
        text += f"   📅 {data.get('date', '?')}\n\n"
    
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
    await state.set_state(AdminStates.waiting_for_user_id)
    await state.update_data(send_type="photo")
    await message.answer(
        "📸 *Введите ID пользователя:*\n\nID можно найти в списке клиентов",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="🔙 Отмена")]], resize_keyboard=True
        )
    )

@dp.message(F.text == "💬 Отправить сообщение")
async def admin_send_message(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(AdminStates.waiting_for_user_id)
    await state.update_data(send_type="text")
    await message.answer(
        "💬 *Введите ID пользователя:*",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="🔙 Отмена")]], resize_keyboard=True
        )
    )

@dp.message(F.text == "🔙 Отмена")
async def cancel_admin(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Отменено", reply_markup=admin_menu)

@dp.message(AdminStates.waiting_for_user_id)
async def get_user_id(message: Message, state: FSMContext):
    if message.text == "🔙 Отмена":
        await state.clear()
        await message.answer("Отменено", reply_markup=admin_menu)
        return
    
    try:
        user_id = int(message.text)
        data = await state.get_data()
        send_type = data.get("send_type")
        
        if send_type == "photo":
            await state.update_data(target_user_id=user_id)
            await state.set_state(AdminStates.waiting_for_design_photo)
            await message.answer(
                f"📸 *Отправьте фото* для пользователя `{user_id}`",
                parse_mode="Markdown",
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=[[KeyboardButton(text="🔙 Отмена")]], resize_keyboard=True
                )
            )
        else:
            await state.update_data(target_user_id=user_id)
            await state.set_state(AdminStates.waiting_for_message_text)
            await message.answer(
                f"💬 *Введите текст* для пользователя `{user_id}`",
                parse_mode="Markdown",
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=[[KeyboardButton(text="🔙 Отмена")]], resize_keyboard=True
                )
            )
    except ValueError:
        await message.answer("❌ Неверный ID, введите число")

@dp.message(AdminStates.waiting_for_design_photo, F.photo)
async def send_design_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("target_user_id")
    
    try:
        await bot.send_photo(
            chat_id=user_id,
            photo=message.photo[-1].file_id,
            caption="🎉 *Ваш дизайн-проект готов!*\n\nСпасибо, что выбрали нас! 🏠",
            parse_mode="Markdown"
        )
        await message.answer(f"✅ *Отправлено* пользователю `{user_id}`", parse_mode="Markdown")
    except Exception as e:
        await message.answer(f"❌ *Ошибка:* {e}", parse_mode="Markdown")
    
    await state.clear()
    await message.answer("Вернулись в админ-меню", reply_markup=admin_menu)

@dp.message(AdminStates.waiting_for_message_text)
async def send_message_text(message: Message, state: FSMContext):
    if message.text == "🔙 Отмена":
        await state.clear()
        await message.answer("Отменено", reply_markup=admin_menu)
        return
    
    data = await state.get_data()
    user_id = data.get("target_user_id")
    text = message.text
    
    try:
        await bot.send_message(
            chat_id=user_id,
            text=f"✉️ *Сообщение от дизайнера:*\n\n{text}\n\n— {PROJECT_NAME}",
            parse_mode="Markdown"
        )
        await message.answer(f"✅ *Отправлено* пользователю `{user_id}`", parse_mode="Markdown")
    except Exception as e:
        await message.answer(f"❌ *Ошибка:* {e}", parse_mode="Markdown")
    
    await state.clear()
    await message.answer("Вернулись в админ-меню", reply_markup=admin_menu)

@dp.message(AdminStates.waiting_for_design_photo)
async def wrong_photo_input(message: Message):
    if message.text == "🔙 Отмена":
        await cancel_admin(message, AdminStates.waiting_for_design_photo)
    else:
        await message.answer("❌ Отправьте фото или нажмите «Отмена»")

# ========== ОПРОС КЛИЕНТА ==========
@dp.message(F.text == "🆕 Новый проект")
async def new_project(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("📋 *Вопрос 1/8: Какую комнату хотите оформить?*", parse_mode="Markdown", reply_markup=nav_kb)
    await message.answer(
        "Выберите:",
        reply_markup=inline_buttons(["Гостиная", "Спальня", "Кухня", "Детская", "Ванная", "Кабинет"], "room", 2)
    )
    await state.set_state(Form.waiting_for_room)

@dp.callback_query(Form.waiting_for_room, F.data.startswith("room_"))
async def q_room(call: CallbackQuery, state: FSMContext):
    await state.update_data(room=call.data.split("_")[1])
    await call.message.delete()
    await call.message.answer("📏 *Вопрос 2/8: Площадь комнаты?*", parse_mode="Markdown", reply_markup=nav_kb)
    await call.message.answer("Выберите:", reply_markup=inline_buttons(["До 12 м²", "12-20 м²", "20+ м²", "Не знаю"], "area", 2))
    await state.set_state(Form.waiting_for_area)
    await call.answer()

@dp.callback_query(Form.waiting_for_area, F.data.startswith("area_"))
async def q_area(call: CallbackQuery, state: FSMContext):
    await state.update_data(area=call.data.split("_")[1])
    await call.message.delete()
    await call.message.answer("🪟 *Вопрос 3/8: Сколько окон?*", parse_mode="Markdown", reply_markup=nav_kb)
    await call.message.answer("Выберите:", reply_markup=inline_buttons(["Нет окон", "1 окно", "2 окна", "Больше 2"], "windows", 2))
    await state.set_state(Form.waiting_for_windows)
    await call.answer()

@dp.callback_query(Form.waiting_for_windows, F.data.startswith("windows_"))
async def q_windows(call: CallbackQuery, state: FSMContext):
    await state.update_data(windows=call.data.split("_")[1])
    await call.message.delete()
    await call.message.answer("🎨 *Вопрос 4/8: Какой стиль?*", parse_mode="Markdown", reply_markup=nav_kb)
    await call.message.answer("Выберите:", reply_markup=inline_buttons(["Современный", "Минимализм", "Лофт", "Скандинавский"], "style", 2))
    await state.set_state(Form.waiting_for_style)
    await call.answer()

@dp.callback_query(Form.waiting_for_style, F.data.startswith("style_"))
async def q_style(call: CallbackQuery, state: FSMContext):
    await state.update_data(style=call.data.split("_")[1])
    await call.message.delete()
    await call.message.answer("🧘 *Вопрос 5/8: Какое настроение?*", parse_mode="Markdown", reply_markup=nav_kb)
    await call.message.answer("Выберите:", reply_markup=inline_buttons(["Уютное", "Строгое", "Романтичное", "Яркое"], "mood", 2))
    await state.set_state(Form.waiting_for_mood)
    await call.answer()

@dp.callback_query(Form.waiting_for_mood, F.data.startswith("mood_"))
async def q_mood(call: CallbackQuery, state: FSMContext):
    await state.update_data(mood=call.data.split("_")[1])
    await call.message.delete()
    await call.message.answer("💰 *Вопрос 6/8: Бюджет?*", parse_mode="Markdown", reply_markup=nav_kb)
    await call.message.answer("Выберите:", reply_markup=inline_buttons(["Эконом", "Средний", "Премиум", "Без разницы"], "budget", 2))
    await state.set_state(Form.waiting_for_budget)
    await call.answer()

@dp.callback_query(Form.waiting_for_budget, F.data.startswith("budget_"))
async def q_budget(call: CallbackQuery, state: FSMContext):
    await state.update_data(budget=call.data.split("_")[1])
    await call.message.delete()
    await call.message.answer("🎨 *Вопрос 7/8: Желаемые цвета?* (напишите через запятую)", parse_mode="Markdown", reply_markup=nav_kb)
    await state.set_state(Form.waiting_for_colors)
    await call.answer()

@dp.message(Form.waiting_for_colors)
async def q_colors(msg: Message, state: FSMContext):
    await state.update_data(colors=msg.text)
    await msg.answer("📸 *Вопрос 8/8: Отправьте фото комнаты*", parse_mode="Markdown", reply_markup=nav_kb)
    await state.set_state(Form.waiting_for_photo)

@dp.message(Form.waiting_for_photo, F.photo)
async def get_photo(msg: Message, state: FSMContext):
    data = await state.get_data()
    photo_id = msg.photo[-1].file_id
    
    user_forms[str(msg.from_user.id)] = {
        'user_id': msg.from_user.id,
        'name': msg.from_user.full_name,
        'username': msg.from_user.username,
        'room': data.get('room'),
        'area': data.get('area'),
        'windows': data.get('windows'),
        'style': data.get('style'),
        'mood': data.get('mood'),
        'budget': data.get('budget'),
        'colors': data.get('colors'),
        'photo_id': photo_id,
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    save_forms()
    
    caption = f"""
📋 *НОВАЯ ЗАЯВКА*

🏠 {data.get('room')} | {data.get('area')} | {data.get('windows')}
🎨 {data.get('style')} | {data.get('mood')} | {data.get('budget')}
🎨 Цвета: {data.get('colors')}

👤 {msg.from_user.full_name}
🆔 `{msg.from_user.id}`
"""
    
    for admin_id in ADMIN_IDS:
        await bot.send_photo(admin_id, photo_id, caption=caption, parse_mode="Markdown")
    
    await msg.answer("✅ *Заявка отправлена!*", parse_mode="Markdown", reply_markup=main_menu)
    if is_admin(msg.from_user.id):
        await show_admin_menu(msg)
    await state.clear()

@dp.message(Form.waiting_for_photo)
async def wrong_input(msg: Message):
    await msg.answer("❌ Отправьте фото комнаты")

# ========== ЗАПУСК ==========
async def main():
    print(f"🤖 {PROJECT_NAME} запущен!")
    print(f"👑 Админы: {ADMIN_IDS}")
    print(f"📂 Загружено заявок: {len(user_forms)}")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
