import asyncio
import logging
from typing import Dict
from datetime import datetime
import os

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties

# ========== НАСТРОЙКИ ==========
BOT_TOKEN = "8789237062:AAE03_Lw4-HO9cmxVn44-b4XHASCV-4Li50"

# 👇 СПИСОК АДМИНОВ
ADMIN_IDS = [
    1031022066, 480615667  # твой ID
]

PROJECT_NAME = "🏠 Будущий дом"
# ================================

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="Markdown"))
dp = Dispatcher()
user_forms: Dict[int, Dict] = {}

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

# ========== КЛАВИАТУРЫ ==========
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🆕 Новый проект")],
        [KeyboardButton(text="❓ Помощь"), KeyboardButton(text="ℹ️ О проекте")]
    ],
    resize_keyboard=True
)

nav_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="❌ Отмена"), KeyboardButton(text="🏠 Меню")]],
    resize_keyboard=True
)

# ========== СОСТОЯНИЯ ==========
class Form(StatesGroup):
    q1_room = State()
    q2_area = State()
    q3_windows = State()
    q4_style = State()
    q5_mood = State()
    q6_budget = State()
    q7_colors_like = State()
    q8_colors_dislike = State()
    q9_light_dark = State()
    q10_zones = State()
    q11_people = State()
    q12_lighting = State()
    q13_furniture = State()
    q14_appliances = State()
    q15_eco = State()
    q16_pets = State()
    q17_dislike = State()
    q18_like = State()
    q19_confirm = State()
    q20_photo = State()

def inline_buttons(options, prefix, cols=2):
    builder = InlineKeyboardBuilder()
    for opt in options:
        builder.button(text=opt, callback_data=f"{prefix}_{opt}")
    builder.adjust(cols)
    return builder.as_markup()

# ========== КОМАНДЫ ==========
@dp.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"{PROJECT_NAME}\n\n🌟 Добро пожаловать!\n\nЯ задам вопросы о вашей комнате.\n\nНажми «Новый проект», чтобы начать.",
        reply_markup=main_menu
    )

@dp.message(F.text == "🏠 Меню")
async def menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Главное меню", reply_markup=main_menu)

@dp.message(F.text == "❌ Отмена")
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Опрос отменён", reply_markup=main_menu)

@dp.message(F.text == "❓ Помощь")
async def help_cmd(message: Message):
    await message.answer("Нажми «Новый проект» и отвечай на вопросы. В конце пришли 1-3 фото комнаты.")

@dp.message(F.text == "ℹ️ О проекте")
async def about(message: Message):
    await message.answer(f"{PROJECT_NAME} — профессиональный дизайн интерьера.")

@dp.message(F.text == "🆕 Новый проект")
async def new_project(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("📋 *Вопрос 1/20: Какую комнату вы хотите оформить?*", parse_mode="Markdown", reply_markup=nav_kb)
    await message.answer(
        "Выберите:",
        reply_markup=inline_buttons(["Гостиная", "Спальня", "Кухня", "Детская", "Ванная", "Кабинет", "Прихожая", "Балкон"], "room", 2)
    )
    await state.set_state(Form.q1_room)

@dp.callback_query(Form.q1_room, F.data.startswith("room_"))
async def q1(call: CallbackQuery, state: FSMContext):
    await state.update_data(room=call.data.split("_")[1])
    await call.message.delete()
    await call.message.answer("📏 *Вопрос 2/20: Площадь комнаты?*", parse_mode="Markdown", reply_markup=nav_kb)
    await call.message.answer("Выберите:", reply_markup=inline_buttons(["До 12 м²", "12-20 м²", "20+ м²", "Не знаю"], "area", 2))
    await state.set_state(Form.q2_area)
    await call.answer()

@dp.callback_query(Form.q2_area, F.data.startswith("area_"))
async def q2(call: CallbackQuery, state: FSMContext):
    await state.update_data(area=call.data.split("_")[1])
    await call.message.delete()
    await call.message.answer("🪟 *Вопрос 3/20: Сколько окон?*", parse_mode="Markdown", reply_markup=nav_kb)
    await call.message.answer("Выберите:", reply_markup=inline_buttons(["Нет окон", "1 окно", "2 окна", "Больше 2"], "windows", 2))
    await state.set_state(Form.q3_windows)
    await call.answer()

@dp.callback_query(Form.q3_windows, F.data.startswith("windows_"))
async def q3(call: CallbackQuery, state: FSMContext):
    await state.update_data(windows=call.data.split("_")[1])
    await call.message.delete()
    await call.message.answer("🎨 *Вопрос 4/20: Какой стиль?*", parse_mode="Markdown", reply_markup=nav_kb)
    await call.message.answer("Выберите:", reply_markup=inline_buttons(["Современный", "Минимализм", "Лофт", "Скандинавский", "Классика", "Прованс", "Бохо", "Эко-стиль"], "style", 2))
    await state.set_state(Form.q4_style)
    await call.answer()

@dp.callback_query(Form.q4_style, F.data.startswith("style_"))
async def q4(call: CallbackQuery, state: FSMContext):
    await state.update_data(style=call.data.split("_")[1])
    await call.message.delete()
    await call.message.answer("🧘 *Вопрос 5/20: Какое настроение?*", parse_mode="Markdown", reply_markup=nav_kb)
    await call.message.answer("Выберите:", reply_markup=inline_buttons(["Уютное", "Строгое", "Романтичное", "Игривое", "Яркое", "Спокойное", "Минималистичное"], "mood", 2))
    await state.set_state(Form.q5_mood)
    await call.answer()

@dp.callback_query(Form.q5_mood, F.data.startswith("mood_"))
async def q5(call: CallbackQuery, state: FSMContext):
    await state.update_data(mood=call.data.split("_")[1])
    await call.message.delete()
    await call.message.answer("💰 *Вопрос 6/20: Бюджет?*", parse_mode="Markdown", reply_markup=nav_kb)
    await call.message.answer("Выберите:", reply_markup=inline_buttons(["Эконом", "Средний", "Премиум", "Без разницы"], "budget", 2))
    await state.set_state(Form.q6_budget)
    await call.answer()

@dp.callback_query(Form.q6_budget, F.data.startswith("budget_"))
async def q6(call: CallbackQuery, state: FSMContext):
    await state.update_data(budget=call.data.split("_")[1])
    await call.message.delete()
    await call.message.answer("🎨 *Вопрос 7/20: Желаемые цвета?* (перечислите через запятую)", parse_mode="Markdown", reply_markup=nav_kb)
    await state.set_state(Form.q7_colors_like)
    await call.answer()

@dp.message(Form.q7_colors_like)
async def q7(msg: Message, state: FSMContext):
    await state.update_data(colors_like=msg.text)
    await msg.answer("🚫 *Вопрос 8/20: Нежелаемые цвета?* (напишите «нет» если таких нет)", parse_mode="Markdown", reply_markup=nav_kb)
    await state.set_state(Form.q8_colors_dislike)

@dp.message(Form.q8_colors_dislike)
async def q8(msg: Message, state: FSMContext):
    text = "нет" if msg.text.lower() in ["нет", "пропустить"] else msg.text
    await state.update_data(colors_dislike=text)
    await msg.answer("☯️ *Вопрос 9/20: Светлые или тёмные тона?*", parse_mode="Markdown", reply_markup=nav_kb)
    await msg.answer("Выберите:", reply_markup=inline_buttons(["Светлые", "Тёмные", "Смешанные"], "lightdark", 2))
    await state.set_state(Form.q9_light_dark)

@dp.callback_query(Form.q9_light_dark, F.data.startswith("lightdark_"))
async def q9(call: CallbackQuery, state: FSMContext):
    await state.update_data(light_dark=call.data.split("_")[1])
    await call.message.delete()
    await call.message.answer("📌 *Вопрос 10/20: Какие зоны нужны?* (можно выбрать несколько, потом нажмите «Готово»)", parse_mode="Markdown", reply_markup=nav_kb)
    await call.message.answer("Выберите зоны:", reply_markup=inline_buttons(["Отдых", "Работа", "Приём гостей", "Хранение", "Обеденная", "Спорт"], "zone", 2))
    await state.update_data(zones=[])
    await state.set_state(Form.q10_zones)
    await call.answer()

@dp.callback_query(Form.q10_zones, F.data.startswith("zone_"))
async def zone_choose(call: CallbackQuery, state: FSMContext):
    zone = call.data.split("_")[1]
    data = await state.get_data()
    zones = data.get("zones", [])
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
    await state.set_state(Form.q11_people)
    await call.answer()

@dp.callback_query(Form.q11_people, F.data.startswith("people_"))
async def q11(call: CallbackQuery, state: FSMContext):
    await state.update_data(people=call.data.split("_")[1])
    await call.message.delete()
    await call.message.answer("💡 *Вопрос 12/20: Тип освещения?*", parse_mode="Markdown", reply_markup=nav_kb)
    await call.message.answer("Выберите:", reply_markup=inline_buttons(["Естественное+доп.", "Только верхний", "Мягкий рассеянный", "Яркое белое", "Тёплое жёлтое"], "lighting", 2))
    await state.set_state(Form.q12_lighting)
    await call.answer()

@dp.callback_query(Form.q12_lighting, F.data.startswith("lighting_"))
async def q12(call: CallbackQuery, state: FSMContext):
    await state.update_data(lighting=call.data.split("_")[1])
    await call.message.delete()
    await call.message.answer("🪑 *Вопрос 13/20: Обязательная мебель?* (перечислите через запятую)", parse_mode="Markdown", reply_markup=nav_kb)
    await state.set_state(Form.q13_furniture)
    await call.answer()

@dp.message(Form.q13_furniture)
async def q13(msg: Message, state: FSMContext):
    await state.update_data(furniture=msg.text)
    await msg.answer("🔌 *Вопрос 14/20: Крупная техника?* (нет/перечислить)", parse_mode="Markdown", reply_markup=nav_kb)
    await state.set_state(Form.q14_appliances)

@dp.message(Form.q14_appliances)
async def q14(msg: Message, state: FSMContext):
    await state.update_data(appliances=msg.text)
    await msg.answer("🌿 *Вопрос 15/20: Эко-материалы важны?*", parse_mode="Markdown", reply_markup=nav_kb)
    await msg.answer("Выберите:", reply_markup=inline_buttons(["Да, важны", "Нет, не принципиально"], "eco", 2))
    await state.set_state(Form.q15_eco)

@dp.callback_query(Form.q15_eco, F.data.startswith("eco_"))
async def q15(call: CallbackQuery, state: FSMContext):
    await state.update_data(eco=call.data.split("_")[1])
    await call.message.delete()
    await call.message.answer("🐾 *Вопрос 16/20: Есть питомцы?*", parse_mode="Markdown", reply_markup=nav_kb)
    await call.message.answer("Выберите:", reply_markup=inline_buttons(["Кошка", "Собака", "Грызуны", "Нет"], "pets", 2))
    await state.set_state(Form.q16_pets)
    await call.answer()

@dp.callback_query(Form.q16_pets, F.data.startswith("pets_"))
async def q16(call: CallbackQuery, state: FSMContext):
    await state.update_data(pets=call.data.split("_")[1])
    await call.message.delete()
    await call.message.answer("😞 *Вопрос 17/20: Что не нравится в текущем интерьере?*", parse_mode="Markdown", reply_markup=nav_kb)
    await state.set_state(Form.q17_dislike)
    await call.answer()

@dp.message(Form.q17_dislike)
async def q17(msg: Message, state: FSMContext):
    await state.update_data(dislike=msg.text)
    await msg.answer("❤️ *Вопрос 18/20: Что хотите сохранить из текущего?*", parse_mode="Markdown", reply_markup=nav_kb)
    await state.set_state(Form.q18_like)

@dp.message(Form.q18_like)
async def q18(msg: Message, state: FSMContext):
    await state.update_data(like=msg.text)
    data = await state.get_data()
    zones_text = ', '.join(data.get('zones', []))
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
👥 Человек: {data.get('people')}
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
    await state.set_state(Form.q19_confirm)

# ========== ОБРАБОТКА ФОТО (НОВАЯ ЛОГИКА) ==========
@dp.callback_query(Form.q19_confirm, F.data == "confirm_✅ Да, всё верно")
async def confirm_yes(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    # Инициализируем список фото и счетчик
    await state.update_data(photos=[], photos_count=0, waiting_more=False)
    await state.set_state(Form.q20_photo)
    
    await call.message.answer(
        "📸 *Вопрос 20/20: Отправьте фото комнаты*\n\n"
        "Вы можете отправить 1-3 фото.\n\n"
        "📌 *Как отправить:*\n"
        "• Отправляйте фото по одному\n"
        "• Или сразу несколько в одном сообщении (альбомом)\n\n"
        "После каждого фото я спрошу: добавить ещё или закончить.\n\n"
        "👉 *Отправьте первое фото*",
        parse_mode="Markdown",
        reply_markup=nav_kb
    )
    await call.answer()

@dp.callback_query(Form.q19_confirm, F.data == "confirm_🔄 Начать заново")
async def confirm_no(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await new_project(call.message, state)
    await call.answer()

# Обработка одиночного фото
@dp.message(Form.q20_photo, F.photo)
async def get_photo_single(msg: Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])
    current_count = len(photos)
    
    if current_count >= 3:
        await msg.answer("❌ Вы уже отправили 3 фото. Нажмите «✅ Завершить и отправить»")
        return
    
    # Добавляем фото
    photos.append(msg.photo[-1].file_id)
    await state.update_data(photos=photos)
    current_count = len(photos)
    
    if current_count == 1:
        await msg.answer(f"📸 Фото 1/3 сохранено.")
    
    # Спрашиваем, хочет ли пользователь добавить ещё
    if current_count < 3:
        builder = InlineKeyboardBuilder()
        builder.button(text="➕ Добавить ещё фото", callback_data="add_more_photo")
        builder.button(text="✅ Завершить и отправить", callback_data="finish_and_send")
        builder.adjust(1)
        
        await msg.answer(
            f"📸 Фото {current_count}/3 сохранено.\n\nЧто делаем дальше?",
            reply_markup=builder.as_markup()
        )
        await state.update_data(waiting_more=True)
    else:
        # Достигнут лимит в 3 фото
        await msg.answer("✅ Вы отправили максимальное количество фото (3). Заявка отправляется...")
        await finish_and_send(msg, state)

# Обработка альбома (несколько фото сразу)
@dp.message(Form.q20_photo, F.media_group_id)
async def get_photo_album(msg: Message, state: FSMContext, album: list = None):
    # Получаем все фото из альбома
    if not hasattr(msg, 'media_group_id'):
        return
    
    data = await state.get_data()
    photos = data.get("photos", [])
    
    # Если это первое фото в альбоме, ждём остальные
    if msg.media_group_id not in data.get("processing_albums", {}):
        processing = data.get("processing_albums", {})
        processing[msg.media_group_id] = []
        await state.update_data(processing_albums=processing)
        
        # Ждём 1 секунду для сбора всех фото альбома
        await asyncio.sleep(1)
        
        # Получаем все фото из этого альбома из хранилища
        # (упрощённо: обрабатываем текущее фото)
    
    # Добавляем фото (упрощённо: добавляем каждое фото из альбома по отдельности)
    new_photo = msg.photo[-1].file_id
    if new_photo not in photos:
        photos.append(new_photo)
        await state.update_data(photos=photos)
        await msg.answer(f"📸 Фото {len(photos)}/3 добавлено из альбома.")
    
    # Проверяем лимит
    if len(photos) >= 3:
        await msg.answer("✅ Достигнут лимит в 3 фото. Заявка отправляется...")
        await finish_and_send(msg, state)

# Кнопка "Добавить ещё фото"
@dp.callback_query(F.data == "add_more_photo")
async def add_more_photo(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer(
        "📸 Отправьте следующее фото.\n\n"
        "Можно отправить по одному или сразу несколько.",
        reply_markup=nav_kb
    )
    await state.update_data(waiting_more=False)
    await call.answer()

# Кнопка "Завершить и отправить"
@dp.callback_query(F.data == "finish_and_send")
async def finish_and_send_callback(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await finish_and_send(call.message, state)
    await call.answer()

# Функция отправки заявки
async def finish_and_send(msg: Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])
    
    if len(photos) == 0:
        await msg.answer("❌ Вы не отправили ни одного фото. Отправьте хотя бы 1 фото.")
        return
    
    # Сохраняем данные пользователя
    user_forms[msg.from_user.id] = data
    user_forms[msg.from_user.id]['name'] = msg.from_user.full_name
    user_forms[msg.from_user.id]['username'] = msg.from_user.username or "нет"
    
    zones_text = ', '.join(data.get('zones', []))
    caption = f"""
📋 *НОВАЯ ЗАЯВКА* #{datetime.now().strftime('%Y%m%d%H%M%S')}

🏠 Комната: {data.get('room')}
📏 Площадь: {data.get('area')}
🪟 Окна: {data.get('windows')}
🎨 Стиль: {data.get('style')}
🧘 Настроение: {data.get('mood')}
💰 Бюджет: {data.get('budget')}
🎨 Желаемые цвета: {data.get('colors_like')}
🚫 Нежелаемые: {data.get('colors_dislike')}
☯️ Тональность: {data.get('light_dark')}
📌 Зоны: {zones_text}
👥 Человек: {data.get('people')}
💡 Освещение: {data.get('lighting')}
🪑 Мебель: {data.get('furniture')}
🔌 Техника: {data.get('appliances')}
🌿 Эко: {data.get('eco')}
🐾 Питомцы: {data.get('pets')}
😞 Не нравится: {data.get('dislike')}
❤️ Сохранить: {data.get('like')}

👤 Клиент: {msg.from_user.full_name}
🆔 ID: `{msg.from_user.id}`
📸 Фото: {len(photos)} шт.
"""
    
    # Отправляем ВСЕМ админам
    for admin_id in ADMIN_IDS:
        try:
            # Отправляем первое фото с подписью
            await bot.send_photo(admin_id, photos[0], caption=caption, parse_mode="Markdown")
            # Отправляем остальные фото (если есть)
            for i in range(1, len(photos)):
                await bot.send_photo(admin_id, photos[i])
            print(f"✅ Заявка отправлена админу {admin_id}")
        except Exception as e:
            print(f"❌ Ошибка при отправке админу {admin_id}: {e}")
    
    await msg.answer(
        "✨ *ГОТОВО!* ✨\n\n"
        f"✅ Получено {len(photos)} фото\n\n"
        "Ваша заявка отправлена дизайнерам.\n\n"
        "Спасибо, что выбрали «Будущий дом»! 🏠",
        parse_mode="Markdown",
        reply_markup=main_menu
    )
    await state.clear()

@dp.message(Form.q20_photo)
async def wrong_photo(msg: Message):
    await msg.answer("❌ Пожалуйста, отправьте фото комнаты в формате изображения.")

# ========== АДМИН КОМАНДЫ ==========
@dp.message(Command("answer"))
async def send_design(message: Message):
    if not is_admin(message.from_user.id):
        return
    
    args = message.text.split()
    if len(args) != 2:
        await message.answer("❌ Использование: /answer USER_ID")
        return
    
    try:
        user_id = int(args[1])
        await message.answer(f"📸 Отправьте фото дизайна для пользователя {user_id}")
        
        @dp.message(F.photo)
        async def forward(msg: Message):
            if not is_admin(msg.from_user.id):
                return
            await bot.send_photo(user_id, msg.photo[-1].file_id, 
                                caption="🎉 Ваш дизайн-проект готов! Спасибо, что выбрали «Будущий дом»! 🏠")
            await msg.answer(f"✅ Дизайн отправлен пользователю {user_id}")
            dp.message_handlers.remove(forward)
    except:
        await message.answer("Ошибка: неверный ID")

@dp.message(Command("users"))
async def show_users(message: Message):
    if not is_admin(message.from_user.id):
        return
    
    if not user_forms:
        await message.answer("📭 Нет активных заявок")
        return
    
    text = "📋 *Список клиентов:*\n\n"
    for uid, data in user_forms.items():
        username = data.get('username', 'нет')
        name = data.get('name', '?')
        text += f"🆔 `{uid}` - {name} (@{username})\n"
    
    # Если текст слишком длинный, обрезаем
    if len(text) > 4000:
        text = text[:3500] + "\n\n... (список слишком длинный)"
    
    await message.answer(text, parse_mode="Markdown")

@dp.message(Command("stats"))
async def show_stats(message: Message):
    if not is_admin(message.from_user.id):
        return
    
    stats_text = f"""
📊 *Статистика {PROJECT_NAME}*

👥 Всего заявок: {len(user_forms)}
👑 Количество админов: {len(ADMIN_IDS)}

📋 Список админов:
"""
    for admin_id in ADMIN_IDS:
        stats_text += f"• `{admin_id}`\n"
    
    await message.answer(stats_text, parse_mode="Markdown")

# ========== ЗАПУСК ==========
async def main():
    print(f"🤖 {PROJECT_NAME} запущен!")
    print(f"👑 Админы: {ADMIN_IDS}")
    print(f"📊 Всего админов: {len(ADMIN_IDS)}")
    
    try:
        me = await bot.get_me()
        print(f"✅ Бот подключился! Имя: {me.first_name}")
        print("🚀 Бот работает с новой логикой фото!")
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
