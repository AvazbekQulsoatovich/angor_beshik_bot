import sys

with open('c:/Users/Avaz/Desktop/beshikbot/handlers/finance.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_sell_logic = '''@finance_router.message(F.text.in_({"🛒 Sotuv qilish", "📥 Kirim (Sotuv)"}), StateFilter('*'))
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
        "📥 <b>Sotuv bo'limi (Kirim)</b>\\n\\nMahsulotni tanlang (Sotilganda avtomatik kirim bo'ladi):",
        parse_mode="HTML",
        reply_markup=builder.as_markup()
    )'''

new_sell_logic = '''@finance_router.message(F.text.in_({"🛒 Sotuv qilish", "📥 Kirim (Sotuv)"}), StateFilter('*'))
async def show_sell_categories(message: Message, state: FSMContext):
    await state.clear()
    categories = await db.get_all_categories(active_only=True)
    if not categories:
        await message.answer("⚠️ Hozirda bo'limlar mavjud emas.")
        return

    from keyboards.admin_kb import get_sell_categories_kb
    await message.answer(
        "📥 <b>Sotuv bo'limi (Kirim)</b>\\n\\nQaysi bo'limdagi (kategoriya) mahsulotni sotdingiz?",
        parse_mode="HTML",
        reply_markup=get_sell_categories_kb(categories)
    )

@finance_router.callback_query(F.data == "sell_back_to_cats")
async def sell_back_to_cats(callback: CallbackQuery):
    categories = await db.get_all_categories(active_only=True)
    from keyboards.admin_kb import get_sell_categories_kb
    await callback.message.edit_text(
        "📥 <b>Sotuv bo'limi (Kirim)</b>\\n\\nQaysi bo'limdagi (kategoriya) mahsulotni sotdingiz?",
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
    )'''

content = content.replace(old_sell_logic, new_sell_logic)

with open('c:/Users/Avaz/Desktop/beshikbot/handlers/finance.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Replaced sell logic in finance.py')
