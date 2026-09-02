import sys

with open('c:/Users/Avaz/Desktop/beshikbot/handlers/finance.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_restock_logic = '''@finance_router.message(F.text.in_({"📦 Omborga tovar qo'shish", "📥 Omborga kirim"}), StateFilter('*'))
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
                text=f"{p['title']} ({stock_count} dona qolgan)",
                callback_data=f"restock_select:{p['id']}"
            )
        )
    builder.row(InlineKeyboardButton(text="❌ Yopish", callback_data="admin_close_panel"))

    await message.answer(
        "📦 <b>Omborni to'ldirish (Kirim)</b>\\n\\nQaysi tovardan olib keldingiz? Tanlang:",
        parse_mode="HTML",
        reply_markup=builder.as_markup()
    )'''

new_restock_logic = '''@finance_router.message(F.text.in_({"📦 Omborga tovar qo'shish", "📥 Omborga kirim"}), StateFilter('*'))
async def show_restock_categories(message: Message, state: FSMContext):
    await state.clear()
    categories = await db.get_all_categories(active_only=True)
    if not categories:
        await message.answer("⚠️ Hozirda bo'limlar yo'q.")
        return

    from keyboards.admin_kb import get_restock_categories_kb
    await message.answer(
        "📦 <b>Omborni to'ldirish (Kirim)</b>\\n\\nQaysi bo'limdagi (kategoriya) tovarni olib keldingiz? Tanlang:",
        parse_mode="HTML",
        reply_markup=get_restock_categories_kb(categories)
    )

@finance_router.callback_query(F.data == "restock_back_to_cats")
async def restock_back_to_cats(callback: CallbackQuery):
    categories = await db.get_all_categories(active_only=True)
    from keyboards.admin_kb import get_restock_categories_kb
    await callback.message.edit_text(
        "📦 <b>Omborni to'ldirish (Kirim)</b>\\n\\nQaysi bo'limdagi (kategoriya) tovarni olib keldingiz? Tanlang:",
        parse_mode="HTML",
        reply_markup=get_restock_categories_kb(categories)
    )

@finance_router.callback_query(F.data.startswith("restock_cat:"))
async def restock_cat_selected(callback: CallbackQuery):
    cat_id = int(callback.data.split(":")[1])
    products = await db.get_products_by_category(cat_id, active_only=True, limit=100)
    if not products:
        await callback.answer("⚠️ Bu bo'limda mahsulot yo'q!", show_alert=True)
        return
        
    from keyboards.admin_kb import get_restock_products_list_kb
    await callback.message.edit_text(
        "Qaysi tovardan olib keldingiz? Tanlang:",
        reply_markup=get_restock_products_list_kb(products)
    )'''

content = content.replace(old_restock_logic, new_restock_logic)

with open('c:/Users/Avaz/Desktop/beshikbot/handlers/finance.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Replaced restock logic in finance.py')
