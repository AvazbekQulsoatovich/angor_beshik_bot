import re

with open('handlers/admin.py', 'r', encoding='utf-8') as f:
    content = f.read()

# For Adding Product
add_desc_str = """@admin_router.message(AdminProductStates.waiting_for_description)
async def product_desc(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(AdminProductStates.waiting_for_cost_price)
    await message.answer("Tannarxi (qanchaga kelganini) raqamda kiriting (Masalan: 500000):")

@admin_router.message(AdminProductStates.waiting_for_cost_price)
async def product_cost_price(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Faqat raqam kiriting!")
        return
    await state.update_data(cost_price=int(message.text))
    await state.set_state(AdminProductStates.waiting_for_price)
    await message.answer("Sotilish narxini kiriting (Mijozga ko'rinadigan, masalan: 800 000 so'm):")"""

content = re.sub(
    r"@admin_router\.message\(AdminProductStates\.waiting_for_description\)\s+async def product_desc\(message: Message, state: FSMContext\):\s+await state\.update_data\(description=message\.text\)\s+await state\.set_state\(AdminProductStates\.waiting_for_price\)\s+await message\.answer\(\"Narxini kiriting:\"\)",
    add_desc_str,
    content
)

# For Editing Product
edit_desc_str = """@admin_router.message(AdminProductEditStates.waiting_for_description)
async def admin_edit_desc(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(AdminProductEditStates.waiting_for_cost_price)
    await message.answer("YANGI tannarxini (qanchaga kelganini) raqamda kiriting (Masalan: 500000):")

@admin_router.message(AdminProductEditStates.waiting_for_cost_price)
async def admin_edit_cost_price(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Faqat raqam kiriting!")
        return
    await state.update_data(cost_price=int(message.text))
    await state.set_state(AdminProductEditStates.waiting_for_price)
    await message.answer("YANGI sotilish narxini kiriting (Mijozga ko'rinadigan):")"""

content = re.sub(
    r"@admin_router\.message\(AdminProductEditStates\.waiting_for_description\)\s+async def admin_edit_desc\(message: Message, state: FSMContext\):\s+await state\.update_data\(description=message\.text\)\s+await state\.set_state\(AdminProductEditStates\.waiting_for_price\)\s+await message\.answer\(\"YANGI narxini kiriting:\"\)",
    edit_desc_str,
    content
)

# Replace DB call for add product
content = content.replace(
    'await db.add_product(data["category_id"], data["title"], data["description"], data["price"], data["photos"], in_stock)',
    'await db.add_product(data["category_id"], data["title"], data["description"], data["price"], data["cost_price"], data["photos"], in_stock)'
)

# Replace DB call for edit product
content = content.replace(
    'await db.update_product_all(data["product_id"], data["title"], data["description"], data["price"], in_stock, photos)',
    'await db.update_product_all(data["product_id"], data["title"], data["description"], data["price"], data["cost_price"], in_stock, photos)'
)

with open('handlers/admin.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated admin.py")
