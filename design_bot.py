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

# 👇 СПИСОК АДМИНОВ (добавляй ID через запятую)
ADMIN_IDS = [
    1031022066,   # твой ID
    # 987654321,   # ID второго админа (раскомментируй и вставь)
    # 555555555,   # ID третьего админа
]

PROJECT_NAME = "🏠 Будущий дом"
# ================================

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="Markdown"))
dp = Dispatcher()
user_forms: Dict[int, Dict] = {}

# Функция проверки админа
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

# ========== ОБРАБОТКА ФОТО ==========
@dp.callback_query(Form.q19_confirm, F.data == "confirm_✅ Да, всё верно")
async def confirm_yes(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer(
        "📸 *Вопрос 20/20: Пришлите 1-3 фото комнаты*\n\nОтправляйте фото по одному. После загрузки всех фото нажмите «✅ Готово, отправить»",
        parse_mode="Markdown",
        reply_markup=nav_kb
    )
    
    await state.update_data(photos=[])
    await state.set_state(Form.q20_photo)
    
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Готово, отправить", callback_data="photos_done")
    await call.message.answer("👇 Когда загрузите все фото, нажмите кнопку:", reply_markup=builder.as_markup())
    
    await call.answer()

@dp.callback_query(Form.q19_confirm, F.data == "confirm_🔄 Начать заново")
async def confirm_no(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await new_project(call.message, state)
    await call.answer()

@dp.message(Form.q20_photo, F.photo)
async def get_photo(msg: Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])
    
    if len(photos) >= 3:
        await msg.answer("❌ Вы уже загрузили 3 фото. Нажмите «Готово, отправить»")
        return
    
    photos.append(msg.photo[-1].file_id)
    await state.update_data(photos=photos)
    
    remaining = 3 - len(photos)
    await msg.answer(f"📸 Фото {len(photos)}/3 сохранено. Осталось {remaining}.")

@dp.callback_query(F.data == "photos_done")
async def photos_done(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])
    
    if len(photos) == 0:
        await call.message.answer("❌ Вы не загрузили ни одного фото. Отправьте хотя бы 1 фото.")
        await call.answer()
        return
    
    user_forms[call.from_user.id] = data
    user_forms[call.from_user.id]['name'] = call.from_user.full_name
    
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

👤 Клиент: {call.from_user.full_name}
🆔 ID: `{call.from_user.id}`
📸 Фото: {len(photos)} шт.
"""
    
    # Отправляем ВСЕМ админам
    for admin_id in ADMIN_IDS:
        try:
            for i, photo_id in enumerate(photos):
                if i == 0:
                    await bot.send_photo(admin_id, photo_id, caption=caption, parse_mode="Markdown")
                else:
                    await bot.send_photo(admin_id, photo_id)
            print(f"✅ Заявка отправлена админу {admin_id}")
        except Exception as e:
            print(f"❌ Ошибка при отправке админу {admin_id}: {e}")
    
    await call.message.edit_text(
        "✨ *ГОТОВО!* ✨\n\nВаша заявка отправлена дизайнерам.\n\nСпасибо, что выбрали «Будущий дом»! 🏠",
        parse_mode="Markdown",
        reply_markup=main_menu
    )
    await state.clear()
    await call.answer()

@dp.message(Form.q20_photo)
async def wrong_photo(msg: Message):
    await msg.answer("❌ Отправьте фото комнаты.")

# ========== АДМИН КОМАНДЫ (для всех админов) ==========
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
            await bot.send_photo(user_id, msg.photo[-1].file_id, caption="🎉 Ваш дизайн-проект готов! 🏠")
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
        text += f"🆔 `{uid}` - {data.get('name', '?')}\n"
    await message.answer(text, parse_mode="Markdown")

@dp.message(Command("stats"))
async def show_stats(message: Message):
    if not is_admin(message.from_user.id):
        return
    
    stats_text = f"""
📊 *Статистика*

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
        print("🚀 Бот работает!")
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
