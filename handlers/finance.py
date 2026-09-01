from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from database import db
from keyboards.admin_kb import get_finance_kb

finance_router = Router()

class FinanceStates(StatesGroup):
    waiting_for_income_amount = State()
    waiting_for_income_desc = State()
    waiting_for_expense_amount = State()
    waiting_for_expense_desc = State()

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
        f"💰 Sof foyda (Qolgan pul): <b>{stats['net_profit']:,} so'm</b>\n\n"
        f"📈 Bugungi kunlik savdo: <b>{stats['daily_income']:,} so'm</b>\n"
        f"📦 Omborxonadagi tovarlar qiymati (Tannarx bo'yicha): <b>{stats['inventory_value']:,} so'm</b>\n\n"
    )
    
    if top_products:
        text += "🔥 <b>Eng ko'p sotilganlar:</b>\n"
        for p in top_products:
            text += f"▪️ {p['title']} - {p['sales_count']} marta\n"
            
    if worst_products:
        text += "\n🧊 <b>Eng kam sotilganlar:</b>\n"
        for p in worst_products:
            text += f"▪️ {p['title']} - {p['sales_count']} marta\n"
            
    await message.answer(text, parse_mode="HTML", reply_markup=get_finance_kb())

@finance_router.callback_query(F.data == "fin_add_income")
async def fin_add_inc(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FinanceStates.waiting_for_income_amount)
    await callback.message.answer("Kirim summasini faqat raqamda kiriting (Masalan: 150000):")
    await callback.answer()

@finance_router.message(FinanceStates.waiting_for_income_amount)
async def fin_inc_amount(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Iltimos, faqat raqam kiriting!")
        return
    await state.update_data(amount=int(message.text))
    await state.set_state(FinanceStates.waiting_for_income_desc)
    await message.answer("Nima uchun kirim qilinganini yozing (Masalan: Beshik sotildi):")

@finance_router.message(FinanceStates.waiting_for_income_desc)
async def fin_inc_desc(message: Message, state: FSMContext):
    data = await state.get_data()
    amount = data['amount']
    desc = message.text
    await db.add_transaction('income', amount, desc)
    await state.clear()
    await message.answer(f"✅ Kirim saqlandi: {amount:,} so'm - {desc}")

@finance_router.callback_query(F.data == "fin_add_expense")
async def fin_add_exp(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FinanceStates.waiting_for_expense_amount)
    await callback.message.answer("Chiqim (xarajat) summasini faqat raqamda kiriting (Masalan: 50000):")
    await callback.answer()

@finance_router.message(FinanceStates.waiting_for_expense_amount)
async def fin_exp_amount(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Iltimos, faqat raqam kiriting!")
        return
    await state.update_data(amount=int(message.text))
    await state.set_state(FinanceStates.waiting_for_expense_desc)
    await message.answer("Nimaga xarajat qilinganini yozing (Masalan: Svet uchun, obetga):")

@finance_router.message(FinanceStates.waiting_for_expense_desc)
async def fin_exp_desc(message: Message, state: FSMContext):
    data = await state.get_data()
    amount = data['amount']
    desc = message.text
    await db.add_transaction('expense', amount, desc)
    await state.clear()
    await message.answer(f"✅ Chiqim saqlandi: {amount:,} so'm - {desc}")
