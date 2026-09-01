def get_finance_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="💵 Kirim (Savdo) qo'shish", callback_data="fin_add_income"))
    builder.row(InlineKeyboardButton(text="💸 Chiqim (Xarajat) qo'shish", callback_data="fin_add_expense"))
    builder.row(InlineKeyboardButton(text="❌ Yopish", callback_data="admin_close_panel"))
    return builder.as_markup()
