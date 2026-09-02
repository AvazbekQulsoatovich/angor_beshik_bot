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

# ─── Sotuv qilish (Kirim) ──────────────────────────────────────────────────────
@finance_router.message(F.text.in_({"🛒 Sotuv qilish", "📥 Kirim (Sotuv)"}), StateFilter('*'))
async def show_sell_categories(message: Message, state: FSMContext):
    await state.clear()
    categories = await db.get_all_categories(active_only=True)
    if not categories:
        await message.answer("⚠️ Hozirda bo'limlar mavjud emas.")
        return

    from keyboards.admin_kb import get_sell_categories_kb
    await message.answer(
        "📥 <b>Sotuv bo'limi (Kirim)</b>\n\nQaysi bo'limdagi (kategoriya) mahsulotni sotdingiz?",
        parse_mode="HTML",
        reply_markup=get_sell_categories_kb(categories)
    )

@finance_router.callback_query(F.data == "sell_back_to_cats")
async def sell_back_to_cats(callback: CallbackQuery):
    categories = await db.get_all_categories(active_only=True)
    from keyboards.admin_kb import get_sell_categories_kb
    await callback.message.edit_text(
        "📥 <b>Sotuv bo'limi (Kirim)</b>\n\nQaysi bo'limdagi (kategoriya) mahsulotni sotdingiz?",
        parse_mode="HTML",
        reply_markup=get_sell_categories_kb(categories)
    )

@finance_router.callback_query(F.data.startswith("sell_cat:"))
async def sell_cat_selected(callback: CallbackQuery):
    cat_id = int(callback.data.split(":")[1])
    products = await db.get_products_by_category(cat_id, active_only=True, limit=100)
    if not products:
        await callback.answer("⚠️ Bu bo'limda mahsulot yo'q!", show_alert=True)
        return
        
    from keyboards.admin_kb import get_sell_products_list_kb
    await callback.message.edit_text(
        "Sotilgan toverni tanlang (tanlasangiz avtomatik sotuv amalga oshadi):",
        reply_markup=get_sell_products_list_kb(products)
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

    # Parse sale price from price string (extract digits)
    import re
    price_digits = re.sub(r'[^\d]', '', str(product['price']))
    sale_price = int(price_digits) if price_digits else 0
    cost_price = product['cost_price'] or 0
    profit = sale_price - cost_price
    title = product['title']

    # Auto-register sale at product's listed price
    await db.add_transaction('income', sale_price, f"Sotuv: {title}", product_id)

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        f"✅ <b>Kirim (Sotuv) qayd etildi!</b>\n\n"
        f"📦 Mahsulot: <b>{title}</b>\n"
        f"📉 Ombor: <b>{product['in_stock'] - 1} dona</b> qoldi\n"
        f"💵 Tannarxi: <b>{cost_price:,} so'm</b>\n"
        f"💰 Sotilgan narxi: <b>{sale_price:,} so'm</b>\n"
        f"📈 Bu savdodan foyda: <b>{profit:,} so'm</b>",
        parse_mode="HTML",
        reply_markup=get_admin_main_menu()
    )
    await callback.answer()
    await state.clear()

# ─── Moliya Statistikasi ───────────────────────────────────────────────────────
@finance_router.message(F.text.in_({"📊 Moliya va Hisobot", "💰 Moliya va Statistika"}), StateFilter('*'))
async def show_finance_menu(message: Message, state: FSMContext):
    await state.clear()
    stats = await db.get_finances()
    inv = await db.get_inventory_analytics()
    top_products = await db.get_top_products()
    worst_products = await db.get_worst_products()

    text = (
        "📊 <b>MOLIYA VA HISOBOT</b>\n\n"
        "━━━ 💹 UMUMIY BIZNES HOLATI ━━━\n"
        f"💵 Jami sotuvdan tushgan pul: <b>{stats['total_income']:,} so'm</b>\n"
        f"💸 Jami xarajatlar: <b>{stats['total_expense']:,} so'm</b>\n"
        f"📦 Tovar olib kelishga ketgan pul: <b>{stats['total_restock']:,} so'm</b>\n"
        f"💰 Sof foyda: <b>{stats['net_profit']:,} so'm</b>\n\n"
        
        "━━━ 📅 BUGUNGI KUNLIK HISOB ━━━\n"
        f"📥 Bugungi savdo tushumi: <b>{stats['daily_income']:,} so'm</b>\n"
        f"📤 Bugungi kundalik xarajatlar: <b>{stats['daily_expense']:,} so'm</b>\n"
        f"📦 Bugun tovar olishga ketgan pul: <b>{stats['daily_restock']:,} so'm</b>\n"
    )
    
    if stats['daily_expenses_list']:
        text += "\n🧾 <i>Bugungi xarajatlar ro'yxati:</i>\n"
        for exp in stats['daily_expenses_list']:
            text += f"➖ {exp['description']}: {exp['amount']:,} so'm\n"
            
    text += (
        "\n💰 <b>TOZA FOYDA (Faqat bugun uchun):</b>\n"
        f"Bugungi savdodan ko'rilgan foyda (tovar puli chiqib ketganda): <b>{stats['daily_sale_profit']:,} so'm</b>\n"
        f"Shundan bugungi xarajatlar (taksi, obet va h.k) ayrilsa: <b>-{stats['daily_expense']:,} so'm</b>\n"
        f"👉 <b>Cho'ntakka qolgani (Sizga qoldi): {stats['daily_pocket']:,} so'm</b>\n"
        f"<i>(Izoh: Yangi tovar olishga ketgan pul xarajatga kirmaydi, chunki u omboringizda turibdi)</i>\n"
    )
    
    text += (
        "\n━━━ 📦 OMBORDAGI HOLAT ━━━\n"
        f"🏷 Necha xil tovar bor: <b>{inv['total_products']} xil</b>\n"
        f"📦 Jami tovarlar soni: <b>{inv['total_qty']} dona</b>\n"
        f"💸 Ombordagi tovarlar qiymati (Olingan narxida): <b>{inv['total_cost_invested']:,} so'm</b>\n"
        f"💵 Hammasi sotilsa bo'ladigan pul: <b>{inv['total_potential_revenue']:,} so'm</b>\n"
        f"📈 Kutilayotgan toza foyda: <b>{inv['potential_profit']:,} so'm</b>\n\n"
    )
    if top_products:
        text += "🔥 <b>Eng ko'p sotilganlar:</b>\n"
        for p in top_products:
            text += f"  ▪️ {p['title']} — {p['sales_count']} marta\n"

    await message.answer(text, parse_mode="HTML", reply_markup=get_admin_main_menu())

# ─── Qo'lda chiqim qo'shish (Asosiy Menyudan) ───────────────────────────────────────────────────
@finance_router.message(F.text.in_({"💸 Boshqa xarajatlar", "📤 Boshqa xarajatlar", "📤 Chiqim (Xarajat)"}), StateFilter('*'))
async def main_add_exp(message: Message, state: FSMContext):
    await state.set_state(FinanceStates.waiting_for_expense_amount)
    await message.answer("📤 Qancha xarajat qildingiz? Faqat raqam yozing (Masalan: 50000):")



@finance_router.message(FinanceStates.waiting_for_expense_amount)
async def fin_exp_amount(message: Message, state: FSMContext):
    if not message.text or not message.text.isdigit():
        await message.answer("⚠️ Faqat raqam kiriting!")
        return
    await state.update_data(amount=int(message.text))
    await state.set_state(FinanceStates.waiting_for_expense_desc)
    await message.answer("Bu pul nimaga ishlatildi? (Masalan: Tushlikka, Taksiga, Svetga):")

@finance_router.message(FinanceStates.waiting_for_expense_desc)
async def fin_exp_desc(message: Message, state: FSMContext):
    data = await state.get_data()
    amount = data['amount']
    await db.add_transaction('expense', amount, message.text)
    await state.clear()
    await message.answer(f"✅ Chiqim saqlandi: <b>{amount:,} so'm</b> — {message.text}", parse_mode="HTML", reply_markup=get_admin_main_menu())

# ─── Omborga kirim (Restock) ──────────────────────────────────────────────────
class RestockStates(StatesGroup):
    waiting_for_cost_price = State()
    waiting_for_sale_price = State()
    waiting_for_qty = State()

@finance_router.message(F.text.in_({"📦 Omborga tovar qo'shish", "📥 Omborga kirim"}), StateFilter('*'))
async def show_restock_products(message: Message, state: FSMContext):
    await state.clear()
    all_prods = await db.get_all_active_products_for_sale()
    if not all_prods:
        await message.answer("⚠️ Hozirda omborda mahsulot yo'q. Oldin 'Yangi mahsulot' qo'shing.")
        return

    builder = InlineKeyboardBuilder()
    for p in all_prods:
        stock_count = p['in_stock'] if p['in_stock'] > 0 else 0
        builder.row(
            InlineKeyboardButton(
                text=f"📦 {p['title']} ({stock_count} dona)",
                callback_data=f"restock_select:{p['id']}"
            )
        )
    builder.row(InlineKeyboardButton(text="❌ Yopish", callback_data="admin_close_panel"))

    await message.answer(
        "📥 <b>Omborga tovar qo'shish</b>\n\nQaysi tovardan olib keldingiz? Tanlang:",
        parse_mode="HTML",
        reply_markup=builder.as_markup()
    )

@finance_router.callback_query(F.data.startswith("restock_select:"))
async def restock_product_selected(callback: CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split(":")[1])
    product = await db.get_product_by_id(product_id)
    if not product:
        await callback.answer("Mahsulot topilmadi!", show_alert=True)
        return

    await state.update_data(restock_id=product_id, title=product['title'])
    await state.set_state(RestockStates.waiting_for_cost_price)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        f"📦 <b>{product['title']}</b> keldi.\n\n"
        f"💵 Tovarni o'zingiz qanchadan sotib oldingiz? (Masalan: 400000):",
        parse_mode="HTML"
    )
    await callback.answer()

@finance_router.message(RestockStates.waiting_for_cost_price)
async def restock_cost_entered(message: Message, state: FSMContext):
    if not message.text or not message.text.isdigit():
        await message.answer("⚠️ Faqat raqam kiriting!")
        return
    await state.update_data(cost_price=int(message.text))
    await state.set_state(RestockStates.waiting_for_sale_price)
    await message.answer("💰 Xaridorga qanchadan sotamiz? (Masalan: 800000):")

@finance_router.message(RestockStates.waiting_for_sale_price)
async def restock_sale_entered(message: Message, state: FSMContext):
    if not message.text or not message.text.isdigit():
        await message.answer("⚠️ Faqat raqam kiriting (so'm so'zini yozmang)!")
        return
    sale_price = f"{int(message.text):,} so'm"
    await state.update_data(sale_price=sale_price)
    await state.set_state(RestockStates.waiting_for_qty)
    await message.answer("📦 Nechta dona olib keldingiz? (Masalan: 10):")

@finance_router.message(RestockStates.waiting_for_qty)
async def restock_qty_entered(message: Message, state: FSMContext):
    if not message.text or not message.text.isdigit():
        await message.answer("⚠️ Faqat raqam kiriting!")
        return
    qty = int(message.text)
    data = await state.get_data()
    
    await db.add_stock_to_product(data['restock_id'], qty, data['cost_price'], data['sale_price'])
    total_expense = qty * data['cost_price']
    await db.add_transaction('restock', total_expense, f"Omborga kirim: {data['title']} x{qty} dona")
    
    await state.clear()
    await message.answer(
        f"✅ <b>Ombor to'ldirildi!</b>\n\n"
        f"📦 {data['title']}: <b>+{qty} dona</b>\n"
        f"💸 Sarmoya kiritildi (Xarajat emas): <b>{total_expense:,} so'm</b>",
        parse_mode="HTML",
        reply_markup=get_admin_main_menu()
    )
