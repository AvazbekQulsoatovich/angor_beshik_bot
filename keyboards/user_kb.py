from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_main_menu(is_admin=False):
    buttons = [
        [KeyboardButton(text="🛍 Katalog")],
        [KeyboardButton(text="ℹ️ Biz haqimizda"), KeyboardButton(text="👨‍💻 Admin bilan aloqa")]
    ]
    if is_admin:
        buttons.append([KeyboardButton(text="🛠 Admin Panel")])
        
    kb = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    return kb

def get_categories_kb(categories):
    builder = InlineKeyboardBuilder()
    for cat in categories:
        emoji = cat['emoji'] or ""
        name = cat['name']
        builder.row(InlineKeyboardButton(text=f"{emoji} {name}", callback_data=f"cat:{cat['id']}"))
    return builder.as_markup()

def get_product_pagination_kb(category_id, product_id, current_page, total_pages):
    builder = InlineKeyboardBuilder()
    
    # Contact admin button
    builder.row(InlineKeyboardButton(text="💬 Adminga yozish (Buyurtma/Savol)", callback_data=f"contact:{product_id}"))
    
    # Pagination
    nav_buttons = []
    if current_page > 1:
        nav_buttons.append(InlineKeyboardButton(text="◀️ Oldingi", callback_data=f"prod:{category_id}:{current_page-1}"))
    
    nav_buttons.append(InlineKeyboardButton(text=f"📄 {current_page}/{total_pages}", callback_data="ignore"))
    
    if current_page < total_pages:
        nav_buttons.append(InlineKeyboardButton(text="Keyingi ▶️", callback_data=f"prod:{category_id}:{current_page+1}"))
        
    builder.row(*nav_buttons)
    
    # Back to categories
    builder.row(InlineKeyboardButton(text="⬅️ Kategoriyalarga qaytish", callback_data="back_to_cats"))
    
    return builder.as_markup()

def get_cancel_inline_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_action")]
    ])
