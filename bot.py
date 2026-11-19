import asyncio, logging, os
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from products import PRODUCTS

BOT_TOKEN = "9039928333:AAEUWsK5v2KNXXplnFvcWrYeqabJOCS31T0"
MANAGER_ID = 6657705993
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

TEXTS = {
    "uz": {
        "welcome": "Assalomu alaykum! 🕊 <b>Kolibri Water</b> xizmatiga xush kelibsiz.\n🚚 <i>Yetkazib berish xizmati mavjud!</i>\n\nKerakli mahsulotni tanlang:",
        "more": "Yana qaysi mahsulotni savatchaga qo'shamiz?",
        "bad": "Iltimos, pastdagi tugmalardan birini tanlang.",
        "qty": "Nechta (blok yoki dona) kerak? Faqat raqam yozing (masalan: 2):",
        "bad_qty": "To'g'ri raqam kiriting (masalan: 3).",
        "cart": "✅ <b>Savatchaga qo'shildi!</b>\n\n🛒 <b>Savatchangiz:</b>\n{list}\n💰 <b>Jami: {total:,} so'm</b>",
        "add": "➕ Yana qo'shish", "ok": "✅ Buyurtmani rasmiylashtirish", "clr": "🗑 Tozalash",
        "cleared": "🗑 Savatcha tozalandi! Mahsulot tanlang:",
        "phone": "💰 Umumiy summa: <b>{total:,} so'm</b>\nTelefon raqamingizni yuboring:",
        "p_btn": "📞 Telefon raqamni yuborish", "addr": "Manzilni yozing yoki lokatsiya yuboring:",
        "l_btn": "📍 Lokatsiya yuborish", "done": "✅ Buyurtmangiz qabul qilindi! Tez orada menejer bog'lanadi.",
        "new": "🔄 Yana buyurtma berish", "cur": "so'm", "pcs": "ta"
    },
    "ru": {
        "welcome": "Здравствуйте! 🕊 Добро пожаловать в <b>Kolibri Water</b>.\n🚚 <i>Имеется услуга доставки!</i>\n\nВыберите нужный товар:",
        "more": "Какой ещё товар добавим в корзину?",
        "bad": "Пожалуйста, выберите одну из кнопок ниже.",
        "qty": "Сколько (блоков или штук) нужно? Введите только цифру (например: 2):",
        "bad_qty": "Введите правильное число (например: 3).",
        "cart": "✅ <b>Добавлено в корзину!</b>\n\n🛒 <b>Ваша корзина:</b>\n{list}\n💰 <b>Итого: {total:,} сум</b>",
        "add": "➕ Добавить ещё", "ok": "✅ Оформить заказ", "clr": "🗑 Очистить",
        "cleared": "🗑 Корзина очищена! Выберите товар:",
        "phone": "💰 Общая сумма: <b>{total:,} сум</b>\nОтправьте ваш номер телефона:",
        "p_btn": "📞 Отправить номер телефона", "addr": "Напишите адрес или отправьте локацию:",
        "l_btn": "📍 Отправить локацию", "done": "✅ Ваш заказ принят! Скоро менеджер свяжется с вами.",
        "new": "🔄 Сделать новый заказ", "cur": "сум", "pcs": "шт"
    }
}

class Order(StatesGroup):
    lang, prod, qty, menu, phone, addr = State(), State(), State(), State(), State(), State()

def kb_prod(l, has_cart=False):
    b = [[KeyboardButton(text=TEXTS[l]["ok"])]] if has_cart else []
    return ReplyKeyboardMarkup(keyboard=b + [[KeyboardButton(text=k)] for k in PRODUCTS[l]], resize_keyboard=True)

def format_cart(cart, l):
    t = sum(i["q"] * i["p"] for i in cart)
    s = "\n".join(f"{n}. {i['n']} — {i['q']} {TEXTS[l]['pcs']} = <b>{i['q']*i['p']:,} {TEXTS[l]['cur']}</b>" for n, i in enumerate(cart, 1))
    return s, t

@dp.message(lambda m: m.text in ["🔄 Yana buyurtma berish", "🔄 Сделать новый заказ"])
@dp.message(CommandStart())
async def start(m: types.Message, state: FSMContext):
    await state.clear()
    await m.answer("Tilni tanlang / Выберите язык:", reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🇺🇿 O'zbekcha"), KeyboardButton(text="🇷🇺 Русский")]], resize_keyboard=True))
    await state.set_state(Order.lang)

@dp.message(Order.lang)
async def get_lang(m: types.Message, state: FSMContext):
    l = "uz" if m.text == "🇺🇿 O'zbekcha" else "ru" if m.text == "🇷🇺 Русский" else None
    if not l: return await m.answer("Tilni tanlang / Выберите язык:")
    await state.update_data(l=l, cart=[])
    await m.answer(TEXTS[l]["welcome"], parse_mode="HTML", reply_markup=kb_prod(l))
    await state.set_state(Order.prod)

@dp.message(Order.prod)
async def get_prod(m: types.Message, state: FSMContext):
    d = await state.get_data(); l, cart = d["l"], d.get("cart", [])
    if m.text == TEXTS[l]["ok"] and cart:
        _, t = format_cart(cart, l)
        await m.answer(TEXTS[l]["phone"].format(total=t), parse_mode="HTML", reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=TEXTS[l]["p_btn"], request_contact=True)]], resize_keyboard=True))
        return await state.set_state(Order.phone)
    if m.text not in PRODUCTS[l]: return await m.answer(TEXTS[l]["bad"])
    await state.update_data(cp=m.text, cpr=PRODUCTS[l][m.text])
    await m.answer(TEXTS[l]["qty"], reply_markup=ReplyKeyboardRemove())
    await state.set_state(Order.qty)

@dp.message(Order.qty)
async def get_qty(m: types.Message, state: FSMContext):
    d = await state.get_data(); l = d["l"]
    if not m.text.isdigit() or int(m.text) <= 0: return await m.answer(TEXTS[l]["bad_qty"])
    q, cart = int(m.text), d.get("cart", [])
    for i in cart:
        if i["n"] == d["cp"]: i["q"] += q; break
    else: cart.append({"n": d["cp"], "p": d["cpr"], "q": q})
    await state.update_data(cart=cart)
    s, t = format_cart(cart, l)
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=TEXTS[l]["ok"])], [KeyboardButton(text=TEXTS[l]["add"]), KeyboardButton(text=TEXTS[l]["clr"])]], resize_keyboard=True)
    await m.answer(TEXTS[l]["cart"].format(list=s, total=t), parse_mode="HTML", reply_markup=kb)
    await state.set_state(Order.menu)

@dp.message(Order.menu)
async def get_menu(m: types.Message, state: FSMContext):
    d = await state.get_data(); l, cart = d["l"], d.get("cart", [])
    if m.text == TEXTS[l]["add"]:
        await m.answer(TEXTS[l]["more"], reply_markup=kb_prod(l, True)); await state.set_state(Order.prod)
    elif m.text == TEXTS[l]["clr"]:
        await state.update_data(cart=[]); await m.answer(TEXTS[l]["cleared"], reply_markup=kb_prod(l)); await state.set_state(Order.prod)
    elif m.text == TEXTS[l]["ok"] and cart:
        _, t = format_cart(cart, l)
        await m.answer(TEXTS[l]["phone"].format(total=t), parse_mode="HTML", reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=TEXTS[l]["p_btn"], request_contact=True)]], resize_keyboard=True))
        await state.set_state(Order.phone)
    else: await m.answer(TEXTS[l]["bad"])

@dp.message(Order.phone)
async def get_phone(m: types.Message, state: FSMContext):
    d = await state.get_data(); l = d["l"]
    await state.update_data(ph=m.contact.phone_number if m.contact else m.text)
    await m.answer(TEXTS[l]["addr"], reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=TEXTS[l]["l_btn"], request_location=True)]], resize_keyboard=True))
    await state.set_state(Order.addr)

@dp.message(Order.addr)
async def get_addr(m: types.Message, state: FSMContext):
    d = await state.get_data(); l, cart = d["l"], d.get("cart", [])
    s, t = format_cart(cart, l)
    txt = f"🚨 <b>YANGI BUYURTMA ({'UZ' if l=='uz' else 'RU'})!</b>\n👤 {m.from_user.full_name} (@{m.from_user.username or 'yo‘q'})\n📞 {d['ph']}\n\n🛒 <b>Savatcha:</b>\n{s}\n\n💵 <b>JAMI: {t:,} {TEXTS[l]['cur']}</b>\n"
    try:
        if m.location:
            await bot.send_message(MANAGER_ID, txt + "📍 Lokatsiya 👇", parse_mode="HTML")
            await bot.send_location(MANAGER_ID, m.location.latitude, m.location.longitude)
        else: await bot.send_message(MANAGER_ID, txt + f"📍 Manzil: {m.text}", parse_mode="HTML")
    except Exception as e: logging.error(e)
    await m.answer(TEXTS[l]["done"], parse_mode="HTML", reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=TEXTS[l]["new"])]], resize_keyboard=True))
    await state.clear()

async def main():
    logging.basicConfig(level=logging.INFO)
    app = web.Application(); app.router.add_get("/", lambda r: web.Response(text="OK"))
    runner = web.AppRunner(app); await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", int(os.environ.get("PORT", 10000))).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
