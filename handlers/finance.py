from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from database import db
from keyboards.admin_kb import get_finance_kb, get_admin_main_menu

finance_router = Router()

class FinanceStates(StatesGroup):
    waiting_for_income_amount = State()
    waiting_for_income_desc = State()
    waiting_for_expense_amount = State()
    waiting_for_expense_desc = State()

class FinanceSellStates(StatesGroup):
    waiting_for_price = State()

# ─── Sotuv qilish (Sales) ──────────────────────────────────────────────────────
@finance_router.message(F.text == "🛒 Sotuv qilish", StateFilter('*'))
async def show_sell_products(message: Message, state: FSMContext):
    await state.clear()
    all_prods = await db.get_all_active_products_for_sale()
    if not all_prods:
        await message.answer("⚠️ Hozirda omborda mahsulot mavjud emas.")
        return

    builder = InlineKeyboardBuilder()
    for p in all_prods:
        stock_count = p['in_stock'] if p['in_stock'] > 0 else 0
        builder.row(
            InlineKeyboardButton(
                text=f"{'✅' if stock_count > 0 else '❌'} {p['title']} ({stock_count} dona) | {p['price']}",
                callback_data=f"sell:{p['id']}" if stock_count > 0 else "no_stock"
            )
        )
    builder.row(InlineKeyboardButton(text="❌ Yopish", callback_data="admin_close_panel"))

    await message.answer(
        "🛒 <b>Sotuv bo'limi</b>\n\nMahsulotni tanlang (✅ - mavjud, ❌ - tugagan):",
        parse_mode="HTML",
        reply_markup=builder.as_markup()
    )

@finance_router.callback_query(F.data == "no_stock")
async def no_stock_cb(callback: CallbackQuery):
    await callback.answer("❌ Bu mahsulot omborda qolmagan!", show_alert=True)

@finance_router.callback_query(F.data.startswith("sell:"))
async def sell_product_selected(callback: CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split(":")[1])
    product = await db.get_product_by_id(product_id)
    if not product:
        await callback.answer("Mahsulot topilmadi!", show_alert=True)
        return
    if product['in_stock'] <= 0:
        await callback.answer("❌ Bu mahsulot omborda qolmagan!", show_alert=True)
        return

    await state.update_data(sell_product_id=product_id, sell_product_title=product['title'], sell_cost_price=product['cost_price'])
    await state.set_state(FinanceSellStates.waiting_for_price)
    await callback.message.answer(
        f"💰 <b>{product['title']}</b> sotilmoqda.\n\n"
        f"📦 Ombordagi miqdori: <b>{product['in_stock']} dona</b>\n"
        f"💵 Tannarxi: <b>{product['cost_price']:,} so'm</b>\n\n"
        f"Sotilgan narxini raqamda kiriting (Masalan: 800000):",
        parse_mode="HTML"
    )
    await callback.answer()

@finance_router.message(FinanceSellStates.waiting_for_price)
async def sell_price_entered(message: Message, state: FSMContext):
    if not message.text or not message.text.isdigit():
        await message.answer("⚠️ Iltimos, faqat raqam kiriting!")
        return

    data = await state.get_data()
    product_id = data.get('sell_product_id')
    title = data.get('sell_product_title')
    cost_price = data.get('sell_cost_price', 0)
    sale_price = int(message.text)
    profit = sale_price - cost_price

    await db.add_transaction('income', sale_price, f"Sotuv: {title}", product_id)
    await state.clear()

    await message.answer(
        f"✅ <b>Sotuv muvaffaqiyatli qayd etildi!</b>\n\n"
        f"📦 Mahsulot: <b>{title}</b>\n"
        f"💵 Tannarxi: <b>{cost_price:,} so'm</b>\n"
        f"💰 Sotilgan narxi: <b>{sale_price:,} so'm</b>\n"
        f"📈 Ushbu savdodan foyda: <b>{profit:,} so'm</b>",
        parse_mode="HTML",
        reply_markup=get_admin_main_menu()
    )

# ─── Moliya Statistikasi ───────────────────────────────────────────────────────
@finance_router.message(F.text == "💰 Moliya va Statistika", StateFilter('*'))
async def show_finance_menu(message: Message, state: FSMContext):
    await state.clear()
    stats = await db.get_finances()
    top_products = await db.get_top_products()
    worst_products = await db.get_worst_products()

    text = (
        "📊 <b>MOLIYAVIY HISOBOT</b>\n\n"
        f"💵 Umumiy tushum (Kirim): <b>{stats['total_income']:,} so'm</b>\n"
        f"💸 Umumiy xarajat (Chiqim): <b>{stats['total_expense']:,} so'm</b>\n"
        f"💰 Sof foyda: <b>{stats['net_profit']:,} so'm</b>\n\n"
        f"📈 Bugungi savdo: <b>{stats['daily_income']:,} so'm</b>\n"
        f"📦 Omborxona qiymati (tannarx): <b>{stats['inventory_value']:,} so'm</b>\n\n"
    )
    if top_products:
        text += "🔥 <b>Eng ko'p sotilganlar:</b>\n"
        for p in top_products:
            text += f"  ▪️ {p['title']} — {p['sales_count']} marta\n"
    if worst_products:
        text += "\n🧊 <b>Eng kam sotilganlar:</b>\n"
        for p in worst_products:
            text += f"  ▪️ {p['title']} — {p['sales_count']} marta\n"

    await message.answer(text, parse_mode="HTML", reply_markup=get_finance_kb())

# ─── Qo'lda kirim qo'shish ────────────────────────────────────────────────────
@finance_router.callback_query(F.data == "fin_add_income")
async def fin_add_inc(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FinanceStates.waiting_for_income_amount)
    await callback.message.answer("Kirim summasini raqamda kiriting (Masalan: 150000):")
    await callback.answer()

@finance_router.message(FinanceStates.waiting_for_income_amount)
async def fin_inc_amount(message: Message, state: FSMContext):
    if not message.text or not message.text.isdigit():
        await message.answer("⚠️ Faqat raqam kiriting!")
        return
    await state.update_data(amount=int(message.text))
    await state.set_state(FinanceStates.waiting_for_income_desc)
    await message.answer("Nima uchun kirim qilinganini yozing:")

@finance_router.message(FinanceStates.waiting_for_income_desc)
async def fin_inc_desc(message: Message, state: FSMContext):
    data = await state.get_data()
    amount = data['amount']
    await db.add_transaction('income', amount, message.text)
    await state.clear()
    await message.answer(f"✅ Kirim saqlandi: <b>{amount:,} so'm</b> — {message.text}", parse_mode="HTML")

# ─── Qo'lda chiqim qo'shish ───────────────────────────────────────────────────
@finance_router.callback_query(F.data == "fin_add_expense")
async def fin_add_exp(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FinanceStates.waiting_for_expense_amount)
    await callback.message.answer("Chiqim (xarajat) summasini raqamda kiriting (Masalan: 50000):")
    await callback.answer()

@finance_router.message(FinanceStates.waiting_for_expense_amount)
async def fin_exp_amount(message: Message, state: FSMContext):
    if not message.text or not message.text.isdigit():
        await message.answer("⚠️ Faqat raqam kiriting!")
        return
    await state.update_data(amount=int(message.text))
    await state.set_state(FinanceStates.waiting_for_expense_desc)
    await message.answer("Nimaga xarajat qilinganini yozing (Masalan: Svet, obyet):")

@finance_router.message(FinanceStates.waiting_for_expense_desc)
async def fin_exp_desc(message: Message, state: FSMContext):
    data = await state.get_data()
    amount = data['amount']
    await db.add_transaction('expense', amount, message.text)
    await state.clear()
    await message.answer(f"✅ Chiqim saqlandi: <b>{amount:,} so'm</b> — {message.text}", parse_mode="HTML")
