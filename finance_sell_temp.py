
class FinanceSellStates(StatesGroup):
    waiting_for_price = State()

@finance_router.callback_query(F.data.startswith("admin_sell_prod:"))
async def admin_sell_product_cb(callback: CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split(":")[1])
    product = await db.get_product_by_id(product_id)
    if not product:
        await callback.answer("Mahsulot topilmadi!")
        return
    await state.update_data(sell_product_id=product_id, sell_product_title=product['title'])
    await state.set_state(FinanceSellStates.waiting_for_price)
    await callback.message.answer(f"📦 <b>{product['title']}</b> sotildi deb belgilash.\n\nSotilgan narxini raqamda kiriting (Masalan: 800000):", parse_mode="HTML")
    await callback.answer()

@finance_router.message(FinanceSellStates.waiting_for_price, StateFilter('*'))
async def admin_sell_product_price(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Iltimos, faqat raqam kiriting!")
        return
        
    data = await state.get_data()
    product_id = data.get('sell_product_id')
    title = data.get('sell_product_title')
    amount = int(message.text)
    
    await db.add_transaction('income', amount, f"Sotuv: {title}", product_id)
    await state.clear()
    await message.answer(f"✅ Savdo qayd etildi!\n\nMahsulot: {title}\nNarx: {amount:,} so'm")
