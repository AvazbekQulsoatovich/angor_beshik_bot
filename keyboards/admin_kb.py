from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_admin_main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛒 Sotuv qilish (Chiqim)"), KeyboardButton(text="📥 Omborga kirim")],
            [KeyboardButton(text="📤 Boshqa xarajatlar"), KeyboardButton(text="➕ Yangi mahsulot")],
            [KeyboardButton(text="📦 Mahsulotlar (Tahrir)"), KeyboardButton(text="📂 Kategoriyalar")],
            [KeyboardButton(text="📥 So'rovlar"), KeyboardButton(text="👥 Adminlar")],
            [KeyboardButton(text="💰 Moliya va Statistika"), KeyboardButton(text="🏠 Asosiy menyu")]
        ],
        resize_keyboard=True
    )

def get_admin_categories_manage_kb(categories):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="➕ Yangi kategoriya qo'shish", callback_data="admin_add_cat"))
    for cat in categories:
        emoji = cat['emoji'] or ""
        builder.row(
            InlineKeyboardButton(text=f"{emoji} {cat['name']}", callback_data="ignore"),
            InlineKeyboardButton(text="✏️", callback_data=f"admin_edit_cat:{cat['id']}"),
            InlineKeyboardButton(text="🗑", callback_data=f"admin_del_cat:{cat['id']}")
        )
    builder.row(InlineKeyboardButton(text="❌ Yopish", callback_data="admin_close_panel"))
    return builder.as_markup()

def get_admin_products_manage_kb(categories):
    builder = InlineKeyboardBuilder()
    for cat in categories:
        emoji = cat['emoji'] or ""
        builder.row(InlineKeyboardButton(text=f"{emoji} {cat['name']}", callback_data=f"admin_prodcat:{cat['id']}"))
    builder.row(InlineKeyboardButton(text="❌ Yopish", callback_data="admin_close_panel"))
    return builder.as_markup()

def get_admin_products_list_kb(products, category_id):
    builder = InlineKeyboardBuilder()
    for p in products:
        builder.row(
            InlineKeyboardButton(text=f"{p['title']}", callback_data="ignore"),
            InlineKeyboardButton(text="💰 Sotildi", callback_data=f"admin_sell_prod:{p['id']}"),
            InlineKeyboardButton(text="✏️ Tahrir", callback_data=f"admin_edit_prod:{p['id']}"),
            InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"admin_del_prod:{p['id']}")
        )
    builder.row(
        InlineKeyboardButton(text="⬅️ Ortga", callback_data="admin_back_to_prod_cats"),
        InlineKeyboardButton(text="❌ Yopish", callback_data="admin_close_panel")
    )
    return builder.as_markup()

def get_in_stock_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Mavjud"), KeyboardButton(text="⏳ Buyurtma bo'yicha")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_product_preview_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Ha (Saqlash)"), KeyboardButton(text="❌ Bekor qilish")]
        ],
        resize_keyboard=True
    )

def get_reply_to_inquiry_kb(user_id, inquiry_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="↩️ Javob berish", callback_data=f"reply:{user_id}:{inquiry_id}")]
    ])

def get_admin_manage_kb(admins):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="➕ Yangi admin qo'shish", callback_data="admin_add_new_admin"))
    for a in admins:
        builder.row(
            InlineKeyboardButton(text=f"ID: {a}", callback_data="ignore"),
            InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"admin_del_admin:{a}")
        )
    builder.row(InlineKeyboardButton(text="❌ Yopish", callback_data="admin_close_panel"))
    return builder.as_markup()

def get_finance_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="💵 Kirim (Savdo) qo'shish", callback_data="fin_add_income"))
    builder.row(InlineKeyboardButton(text="💸 Chiqim (Xarajat) qo'shish", callback_data="fin_add_expense"))
    builder.row(InlineKeyboardButton(text="❌ Yopish", callback_data="admin_close_panel"))
    return builder.as_markup()
