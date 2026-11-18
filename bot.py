import asyncio
import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

BOT_TOKEN = "9039928333:AAEUWsK5v2KNXXplnFvcWrYeqabJOCS31T0"
MANAGER_ID = 6657705993

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

PRODUCTS = {
    "uz": {
        "💧 Gazsiz 1,5L Premium (Blok 6 dona) - 16 500 so'm": 16500,
        "🫧 Gazli 1,5L Premium (Blok 6 dona) - 16 500 so'm": 16500,
        "💧 Gazsiz 1L Premium (Blok 8 dona) - 16 000 so'm": 16000,
        "🫧 Gazli 1L Premium (Blok 8 dona) - 16 000 so'm": 16000,
        "💧 Gazsiz 0,5L Premium (Blok 15 dona) - 25 500 so'm": 25500,
        "🫧 Gazli 0,5L Premium (Blok 15 dona) - 25 500 so'm": 25500,
        "💧 Gazsiz 1L (Blok 8 dona) - 16 000 so'm": 16000,
        "💧 Gazsiz 0,5L (Blok 12 dona) - 19 200 so'm": 19200,
        "💧 Gazsiz 0,33L (Blok 15 dona) - 21 000 so'm": 21000,
        "💧 Gazsiz 5L (1 dona) - 6 500 so'm": 6500,
        "💧 Gazsiz 10L (1 dona) - 8 500 so'm": 8500,
        "💧 Gazsiz 18,9L Kapsula (1 dona) - 15 000 so'm": 15000,
        "🧴 Bo'sh idish 18,9L (1 dona) - 30 000 so'm": 30000,
        "❄️ Kuler + 2 ta 18,9L suv sovg'a - 1 300 000 so'm": 1300000,
    },
    "ru": {
        "💧 Негазированная 1,5л Premium (Блок 6 шт) - 16 500 сум": 16500,
        "🫧 Газированная 1,5л Premium (Блок 6 шт) - 16 500 сум": 16500,
        "💧 Негазированная 1л Premium (Блок 8 шт) - 16 000 сум": 16000,
        "🫧 Газированная 1л Premium (Блок 8 шт) - 16 000 сум": 16000,
        "💧 Негазированная 0,5л Premium (Блок 15 шт) - 25 500 сум": 25500,
        "🫧 Газированная 0,5л Premium (Блок 15 шт) - 25 500 сум": 25500,
        "💧 Негазированная 1л (Блок 8 шт) - 16 000 сум": 16000,
        "💧 Негазированная 0,5л (Блок 12 шт) - 19 200 сум": 19200,
        "💧 Негазированная 0,33л (Блок 15 шт) - 21 000 сум": 21000,
        "💧 Негазированная 5л (1 шт) - 6 500 сум": 6500,
        "💧 Негазированная 10л (1 шт) - 8 500 сум": 8500,
        "💧 Негазированная 18,9л Капсула (1 шт) - 15 000 сум": 15000,
        "🧴 Пустая бутыль 18,9л (1 шт) - 30 000 сум": 30000,
        "❄️ Кулер + 2 бутыли 18,9л в подарок - 1 300 000 сум": 1300000,
    }
}

TEXTS = {
    "uz": {
        "welcome": "Assalomu alaykum! 🕊 <b>Kolibri Water</b> suv yetkazib berish xizmatiga xush kelibsiz.\n🚚 <i>Yetkazib berish xizmati mavjud!</i>\n\nKerakli mahsulotni tanlang:",
        "choose_btn": "Iltimos, pastdagi tugmalardan birini tanlang.",
        "ask_qty": "Nechta (nechta blok yoki dona) kerak?\nFaqat raqam yozing (masalan: 2):",
        "wrong_qty": "Iltimos, to'g'ri raqam kiriting (masalan: 3).",
        "total_ask_phone": "💰 Mahsulotlar summasi: <b>{total:,} so'm</b>\n🚚 Yetkazib berish xizmati mavjud.\n\nBuyurtmani rasmiylashtirish uchun telefon raqamingizni yuboring:",
        "phone_btn": "📞 Telefon raqamni yuborish",
        "ask_address": "Yetkazib berish manzilini yozing yoki lokatsiya yuboring:",
        "loc_btn": "📍 Lokatsiya yuborish",
        "done": "✅ Buyurtmangiz qabul qilindi! Tez orada <b>Kolibri Water</b> menejeri siz bilan bog'lanadi.\n\nYana buyurtma berish uchun /start ni bosing."
    },
    "ru": {
        "welcome": "Здравствуйте! 🕊 Добро пожаловать в службу доставки воды <b>Kolibri Water</b>.\n🚚 <i>Имеется услуга доставки!</i>\n\nВыберите нужный товар:",
        "choose_btn": "Пожалуйста, выберите одну из кнопок ниже.",
        "ask_qty": "Сколько (блоков или штук) вам нужно?\nВведите только цифру (например: 2):",
        "wrong_qty": "Пожалуйста, введите правильное число (например: 3).",
        "total_ask_phone": "💰 Сумма товаров: <b>{total:,} сум</b>\n🚚 Имеется услуга доставки.\n\nОтправьте ваш номер телефона для оформления заказа:",
        "phone_btn": "📞 Отправить номер телефона",
        "ask_address": "Напишите адрес доставки или отправьте локацию:",
        "loc_btn": "📍 Отправить локацию",
        "done": "✅ Ваш заказ принят! В ближайшее время менеджер <b>Kolibri Water</b> свяжется с вами.\n\nЧтобы сделать новый заказ, нажмите /start."
    }
}

class OrderState(StatesGroup):
    choosing_lang = State()
    choosing_product = State()
    entering_quantity = State()
    entering_phone = State()
    entering_address = State()

def get_lang_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🇺🇿 O'zbekcha"), KeyboardButton(text="🇷🇺 Русский")]],
        resize_keyboard=True
    )

def get_products_keyboard(lang: str):
    buttons = [[KeyboardButton(text=name)] for name in PRODUCTS[lang].keys()]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Tilni tanlang / Выберите язык:",
        reply_markup=get_lang_keyboard()
    )
    await state.set_state(OrderState.choosing_lang)

@dp.message(OrderState.choosing_lang)
async def process_lang(message: types.Message, state: FSMContext):
    if message.text == "🇺🇿 O'zbekcha":
        lang = "uz"
    elif message.text == "🇷🇺 Русский":
        lang = "ru"
    else:
        await message.answer("Iltimos, tilni tanlang / Пожалуйста, выберите язык:")
        return

    await state.update_data(lang=lang)
    await message.answer(
        TEXTS[lang]["welcome"],
        parse_mode="HTML",
        reply_markup=get_products_keyboard(lang)
    )
    await state.set_state(OrderState.choosing_product)

@dp.message(OrderState.choosing_product)
async def process_product(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data["lang"]

    if message.text not in PRODUCTS[lang]:
        await message.answer(TEXTS[lang]["choose_btn"])
        return
    
    await state.update_data(product=message.text, price=PRODUCTS[lang][message.text])
    await message.answer(
        TEXTS[lang]["ask_qty"],
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(OrderState.entering_quantity)

@dp.message(OrderState.entering_quantity)
async def process_quantity(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data["lang"]

    if not message.text.isdigit() or int(message.text) <= 0:
        await message.answer(TEXTS[lang]["wrong_qty"])
        return

    qty = int(message.text)
    total_price = qty * data["price"]
    await state.update_data(quantity=qty, total_price=total_price)
    
    phone_kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=TEXTS[lang]["phone_btn"], request_contact=True)]],
        resize_keyboard=True
    )
    
    await message.answer(
        TEXTS[lang]["total_ask_phone"].format(total=total_price),
        parse_mode="HTML",
        reply_markup=phone_kb
    )
    await state.set_state(OrderState.entering_phone)

@dp.message(OrderState.entering_phone)
async def process_phone(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data["lang"]
    phone = message.contact.phone_number if message.contact else message.text
    await state.update_data(phone=phone)
    
    location_kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=TEXTS[lang]["loc_btn"], request_location=True)]],
        resize_keyboard=True
    )
    
    await message.answer(
        TEXTS[lang]["ask_address"],
        reply_markup=location_kb
    )
    await state.set_state(OrderState.entering_address)

@dp.message(OrderState.entering_address)
async def process_address(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data["lang"]
    user = message.from_user
    lang_label = "O'zbekcha" if lang == "uz" else "Русский"
    
    manager_text = (
        f"🚨 <b>YANGI BUYURTMA ({lang_label})!</b>\n\n"
        f"👤 Mijoz: {user.full_name} (@{user.username or 'yo‘q'})\n"
        f"📞 Telefon: {data['phone']}\n"
        f"💧 Mahsulot: {data['product']}\n"
        f"🔢 Soni: {data['quantity']} ta\n"
        f"💵 Mahsulot summasi: <b>{data['total_price']:,} so'm</b>\n"
    )

    try:
        if message.location:
            manager_text += "📍 Manzil: Quyidagi lokatsiyada 👇"
            await bot.send_message(MANAGER_ID, manager_text, parse_mode="HTML")
            await bot.send_location(MANAGER_ID, message.location.latitude, message.location.longitude)
        else:
            manager_text += f"📍 Manzil: {message.text}"
            await bot.send_message(MANAGER_ID, manager_text, parse_mode="HTML")
    except Exception as e:
        logging.error(f"Menejerga yuborishda xato: {e}")

    await message.answer(
        TEXTS[lang]["done"],
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()

# Render serveri uchun kichik veb-sahifa
async def handle(request):
    return web.Response(text="Kolibri Water Bot ishlamoqda!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    logging.basicConfig(level=logging.INFO)
    await start_web_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
