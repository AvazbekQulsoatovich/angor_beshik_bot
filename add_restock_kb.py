import sys

with open('c:/Users/Avaz/Desktop/beshikbot/keyboards/admin_kb.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_kbs = '''
def get_restock_categories_kb(categories):
    builder = InlineKeyboardBuilder()
    for cat in categories:
        emoji = cat['emoji'] or ""
        builder.row(InlineKeyboardButton(text=f"{emoji} {cat['name']}", callback_data=f"restock_cat:{cat['id']}"))
    builder.row(InlineKeyboardButton(text="❌ Yopish", callback_data="admin_close_panel"))
    return builder.as_markup()

def get_restock_products_list_kb(products):
    builder = InlineKeyboardBuilder()
    for p in products:
        stock_count = p['in_stock'] if p['in_stock'] > 0 else 0
        builder.row(
            InlineKeyboardButton(
                text=f"📦 {p['title']} ({stock_count} dona)",
                callback_data=f"restock_select:{p['id']}"
            )
        )
    builder.row(
        InlineKeyboardButton(text="⬅️ Ortga", callback_data="restock_back_to_cats"),
        InlineKeyboardButton(text="❌ Yopish", callback_data="admin_close_panel")
    )
    return builder.as_markup()
'''

content = content + new_kbs

with open('c:/Users/Avaz/Desktop/beshikbot/keyboards/admin_kb.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Added restock kbs')
