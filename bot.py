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
        "choose_more": "Yana qaysi mahsulotni savatchaga qo'shamiz?",
        "choose_btn": "Iltimos, pastdagi tugmalardan birini tanlang.",
        "ask_qty": "Nechta (nechta blok yoki dona) kerak?\nFaqat raqam yozing (masalan: 2):",
        "wrong_qty": "Iltimos, to'g'ri raqam kiriting (masalan: 3).",
        "added_to_cart": "✅ <b>Savatchaga qo'shildi!</b>\n\n🛒 <b>Sizning savatchangiz:</b>\n{cart_list}\n💰 <b>Jami summa: {total:,} so'm</b>\n\nYana mahsulot qo'shasizmi yoki buyurtmani rasmiylashtiramizmi?",
        "btn_add_more": "➕ Yana mahsulot qo'shish",
        "btn_checkout": "✅ Buyurtmani rasmiylashtirish",
        "btn_clear": "🗑 Savatchani tozalash",
        "cart_cleared": "🗑 Savatcha tozalandi! Qaytadan mahsulot tanlang:",
        "empty_cart": "Savatchangiz bo'sh. Avval mahsulot tanlang:",
        "ask_phone": "💰 Umumiy summa: <b>{total:,} so'm</b>\n🚚 Yetkazib berish xizmati mavjud.\n\nBuyurtmani tasdiqlash uchun telefon raqamingizni yuboring:",
        "phone_btn": "📞 Telefon raqamni yuborish",
        "ask_address": "Yetkazib berish manzilini yozing yoki lokatsiya yuboring:",
        "loc_btn": "📍 Lokatsiya yuborish",
        "done": "✅ Buyurtmangiz qabul qilindi! Tez orada <b>Kolibri Water</b> menejeri siz bilan bog'lanadi.",
        "btn_new_order": "🔄 Yana buyurtma berish",
        "currency": "so'm",
        "pcs": "ta"
    },
    "ru": {
        "welcome": "Здравствуйте! 🕊 Добро пожаловать в службу доставки воды <b>Kolibri Water</b>.\n🚚 <i>Имеется услуга доставки!</i>\n\nВыберите нужный товар:",
        "choose_more": "Какой ещё товар добавим в корзину?",
        "choose_btn": "Пожалуйста, выберите одну из кнопок ниже.",
        "ask_qty": "Сколько (блоков или штук) вам нужно?\nВведите только цифру (например: 2):",
        "wrong_qty": "Пожалуйста, введите правильное число (например: 3).",
        "added_to_cart": "✅ <b>Добавлено в корзину!</b>\n\n🛒 <b>Ваша корзина:</b>\n{cart_list}\n💰 <b>Итоговая сумма: {total:,} сум</b>\n\nДобавить ещё товар или оформить заказ?",
        "btn_add_more": "➕ Добавить ещё товар",
        "btn_checkout": "✅ Оформить заказ",
        "btn_clear": "🗑 Очистить корзину",
        "cart_cleared": "🗑 Корзина очищена! Выберите товар заново:",
        "empty_cart": "Ваша корзина пуста. Сначала выберите товар:",
        "ask_phone": "💰 Общая сумма: <b>{total:,} сум</b>\n🚚 Имеется услуга доставки.\n\nОтправьте ваш номер телефона для подтверждения заказа:",
        "phone_btn": "📞 Отправить номер телефона",
        "ask_address": "Напишите адрес доставки или отправьте локацию:",
        "loc_btn": "📍 Отправить локацию",
        "done": "✅ Ваш заказ принят! В ближайшее время менеджер <b>Kolibri Water</b> свяжется с вами.",
        "btn_new_order": "🔄 Сделать новый заказ",
        "currency": "сум",
        "pcs": "шт"
    }
}

class OrderState(StatesGroup):
    choosing_lang = State()
    choosing_product = State()
    entering_quantity = State()
    cart_menu = State()
    entering_phone = State()
    entering_address = State()

def get_lang_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🇺🇿 O'zbekcha"), KeyboardButton(text="🇷🇺 Русский")]],
        resize_keyboard=True
    )

def get_products_keyboard(lang: str, has_cart: bool = False):
    buttons = []
    if has_cart:
        buttons.append([KeyboardButton(text=TEXTS[lang]["btn_checkout"])])
    for name in PRODUCTS[lang].keys():
        buttons.append([KeyboardButton(text=name)])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_cart_keyboard(lang: str):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=TEXTS[lang]["btn_checkout"])],
            [KeyboardButton(text=TEXTS[lang]["btn_add_more"]), KeyboardButton(text=TEXTS[lang]["btn_clear"])]
        ],
        resize_keyboard=True
    )

def format_cart(cart: list, lang: str):
    lines = []
    total = 0
    curr = TEXTS[lang]["currency"]
    pcs = TEXTS[lang]["pcs"]
    for i, item in enumerate(cart, 1):
        subtotal = item["qty"] * item["price"]
        total += subtotal
        lines.append(f"{i}. {item['name']} — {item['qty']} {pcs} = <b>{subtotal:,} {curr}</b>")
    return "\n".join(lines), total

# "Yana buyurtma berish" tugmasini ham /start kabi qabul qilish
@dp.message(lambda msg: msg.text in ["🔄 Yana buyurtma berish", "🔄 Сделать новый заказ"])
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

    await state.update_data(lang=lang, cart=[])
    await message.answer(
        TEXTS[lang]["welcome"],
        parse_mode="HTML",
        reply_markup=get_products_keyboard(lang, has_cart=False)
    )
    await state.set_state(OrderState.choosing_product)

@dp.message(OrderState.choosing_product)
async def process_product(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data["lang"]
    cart = data.get("cart", [])

    # Agar savatchada narsa bo'lsa va mijoz to'g'ridan-to'g'ri rasmiylashtirishni bossa
    if message.text == TEXTS[lang]["btn_checkout"]:
        if not cart:
            await message.answer(TEXTS[lang]["empty_cart"])
            return
        _, total = format_cart(cart, lang)
        phone_kb = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=TEXTS[lang]["phone_btn"], request_contact=True)]],
            resize_keyboard=True
        )
        await message.answer(
            TEXTS[lang]["ask_phone"].format(total=total),
            parse_mode="HTML",
            reply_markup=phone_kb
        )
        await state.set_state(OrderState.entering_phone)
        return

    if message.text not in PRODUCTS[lang]:
        await message.answer(TEXTS[lang]["choose_btn"])
        return
    
    await state.update_data(current_product=message.text, current_price=PRODUCTS[lang][message.text])
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
    cart = data.get("cart", [])
    
    # Agar bu mahsulot oldin savatchada bo'lsa, sonini qo'shamiz
    found = False
    for item in cart:
        if item["name"] == data["current_product"]:
            item["qty"] += qty
            found = True
            break
    if not found:
        cart.append({
            "name": data["current_product"],
            "price": data["current_price"],
            "qty": qty
        })

