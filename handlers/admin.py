from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from config import ADMIN_IDS
import json

from keyboards.admin_kb import (
    get_admin_main_menu, 
    get_admin_categories_manage_kb, 
    get_in_stock_kb, 
    get_product_preview_kb,
    get_admin_products_manage_kb,
    get_admin_products_list_kb,
    get_admin_manage_kb
)
from keyboards.user_kb import get_cancel_inline_kb
from database import db
from states.admin_states import (
    AdminCategoryStates, 
    AdminProductStates, 
    AdminReplyStates,
    AdminCategoryEditStates,
    AdminProductEditStates,
    AdminManageStates
)

admin_router = Router()

async def get_all_admins():
    db_admins = await db.get_all_admins()
    return list(set(ADMIN_IDS + db_admins))

async def is_admin(user_id):
    admins = await get_all_admins()
    return user_id in admins

@admin_router.message(Command("admin"))
@admin_router.message(F.text == "🛠 Admin Panel")
async def cmd_admin(message: Message):
    if not await is_admin(message.from_user.id):
        return
    await message.answer("🛠 Admin paneliga xush kelibsiz!", reply_markup=get_admin_main_menu())

# --- Manage Admins ---
@admin_router.message(F.text == "👥 Adminlarni boshqarish")
async def manage_admins(message: Message):
    if not await is_admin(message.from_user.id): return
    admins = await get_all_admins()
    await message.answer("👥 Adminlar ro'yxati:", reply_markup=get_admin_manage_kb(admins))

@admin_router.callback_query(F.data == "admin_add_new_admin")
async def add_admin_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminManageStates.waiting_for_new_admin_id)
    await callback.message.answer("Yangi adminning Telegram ID raqamini kiriting:", reply_markup=get_cancel_inline_kb())
    await callback.answer()

@admin_router.message(AdminManageStates.waiting_for_new_admin_id)
async def add_admin_finish(message: Message, state: FSMContext):
    try:
        new_id = int(message.text)
        success = await db.add_admin_db(new_id)
        if success:
            await message.answer(f"✅ Yangi admin qo'shildi (ID: {new_id})")
        else:
            await message.answer("Bunday admin allaqachon bor yoki xatolik yuz berdi.")
    except:
        await message.answer("Faqat raqam kiritilishi shart!")
    await state.clear()
    
@admin_router.callback_query(F.data.startswith("admin_del_admin:"))
async def del_admin(callback: CallbackQuery):
    admin_id = int(callback.data.split(":")[1])
    if admin_id in ADMIN_IDS:
        await callback.answer("Bu asosiy admin! O'chirib bo'lmaydi.", show_alert=True)
        return
    await db.remove_admin_db(admin_id)
    await callback.answer("Admin o'chirildi.")
    admins = await get_all_admins()
    await callback.message.edit_reply_markup(reply_markup=get_admin_manage_kb(admins))

# --- Categories Management ---
@admin_router.message(F.text == "📂 Kategoriyalar")
async def manage_categories(message: Message):
    if not await is_admin(message.from_user.id): return
    categories = await db.get_all_categories(active_only=True)
    await message.answer("📂 Kategoriyalar ro'yxati:", reply_markup=get_admin_categories_manage_kb(categories))

@admin_router.callback_query(F.data == "admin_add_cat")
async def add_category_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminCategoryStates.waiting_for_name)
    await callback.message.answer("Yangi kategoriya nomini kiriting:", reply_markup=get_cancel_inline_kb())
    await callback.answer()

@admin_router.message(AdminCategoryStates.waiting_for_name)
async def add_category_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AdminCategoryStates.waiting_for_emoji)
    await message.answer("Kategoriya uchun emoji kiriting (masalan 🪵):", reply_markup=get_cancel_inline_kb())

@admin_router.message(AdminCategoryStates.waiting_for_emoji)
async def add_category_emoji(message: Message, state: FSMContext):
    data = await state.get_data()
    await db.add_category(data['name'], message.text)
    await state.clear()
    await message.answer(f"✅ Kategoriya qo'shildi!")

@admin_router.callback_query(F.data.startswith("admin_del_cat:"))
async def del_category(callback: CallbackQuery):
    cat_id = int(callback.data.split(":")[1])
    await db.soft_delete_category(cat_id)
    await callback.answer("Kategoriya o'chirildi.")
    categories = await db.get_all_categories(active_only=True)
    await callback.message.edit_reply_markup(reply_markup=get_admin_categories_manage_kb(categories))

@admin_router.callback_query(F.data.startswith("admin_edit_cat:"))
async def edit_category_start(callback: CallbackQuery, state: FSMContext):
    cat_id = int(callback.data.split(":")[1])
    await state.update_data(cat_id=cat_id)
    await state.set_state(AdminCategoryEditStates.waiting_for_name)
    await callback.message.answer("Kategoriyaning YUNGI nomini kiriting:", reply_markup=get_cancel_inline_kb())
    await callback.answer()

@admin_router.message(AdminCategoryEditStates.waiting_for_name)
async def edit_category_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AdminCategoryEditStates.waiting_for_emoji)
    await message.answer("Kategoriya uchun YANGI emoji kiriting:", reply_markup=get_cancel_inline_kb())

@admin_router.message(AdminCategoryEditStates.waiting_for_emoji)
async def edit_category_emoji(message: Message, state: FSMContext):
    data = await state.get_data()
    await db.update_category(data['cat_id'], data['name'], message.text)
    await state.clear()
    await message.answer(f"✅ Kategoriya yangilandi!")

# --- Product Management ---
@admin_router.message(F.text == "➕ Mahsulot qo'shish")
async def add_product_start(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id): return
    categories = await db.get_all_categories(active_only=True)
    if not categories:
        await message.answer("Oldin kategoriya qo'shing!")
        return
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    for cat in categories:
        builder.row(InlineKeyboardButton(text=f"{cat['emoji'] or ''} {cat['name']}", callback_data=f"selcat:{cat['id']}"))
    builder.row(InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_action"))
    
    await state.set_state(AdminProductStates.waiting_for_category)
    await message.answer("Qaysi kategoriyaga mahsulot qo'shamiz?", reply_markup=builder.as_markup())

@admin_router.callback_query(AdminProductStates.waiting_for_category, F.data.startswith("selcat:"))
async def product_cat_selected(callback: CallbackQuery, state: FSMContext):
    cat_id = int(callback.data.split(":")[1])
    await state.update_data(category_id=cat_id, photos=[])
    await state.set_state(AdminProductStates.waiting_for_photos)
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✅ Rasm yuklab bo'ldim", callback_data="done_photos")]])
    await callback.message.answer("Mahsulot rasmini yuboring (bir nechta yuborish mumkin). Tugatgach, pastdagi tugmani bosing.", reply_markup=kb)
    await callback.answer()

import asyncio
photo_upload_lock = asyncio.Lock()

@admin_router.message(AdminProductStates.waiting_for_photos, F.photo)
async def product_photo_received(message: Message, state: FSMContext):
    async with photo_upload_lock:
        data = await state.get_data()
        photos = data.get('photos', [])
        photos.append(message.photo[-1].file_id)
        await state.update_data(photos=photos)
    await message.reply(f"✅ {len(photos)}-rasm qabul qilindi. Yana yuboring yoki '✅ Rasm yuklab bo'ldim' tugmasini bosing.")

@admin_router.callback_query(AdminProductStates.waiting_for_photos, F.data == "done_photos")
async def product_photos_done(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminProductStates.waiting_for_title)
    await callback.message.answer("Beshik nomi / modelini kiriting:")
    await callback.answer()

@admin_router.message(AdminProductStates.waiting_for_title)
async def product_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(AdminProductStates.waiting_for_description)
    await message.answer("Izoh / tavsif kiriting:")

@admin_router.message(AdminProductStates.waiting_for_description)
async def product_desc(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(AdminProductStates.waiting_for_price)
    await message.answer("Narxni kiriting (masalan, 500 000 so'm):")

@admin_router.message(AdminProductStates.waiting_for_price)
async def product_price(message: Message, state: FSMContext):
    await state.update_data(price=message.text)
    await state.set_state(AdminProductStates.waiting_for_stock)
    await message.answer("Mavjudlik holatini tanlang:", reply_markup=get_in_stock_kb())

@admin_router.message(AdminProductStates.waiting_for_stock)
async def product_stock(message: Message, state: FSMContext):
    in_stock = True if message.text == "✅ Mavjud" else False
    await state.update_data(in_stock=in_stock)
    
    data = await state.get_data()
    stock_text = "✅ Mavjud" if in_stock else "⏳ Buyurtma bo'yicha"
    text = (
        f"🏷 <b>{data['title']}</b>\n\n"
        f"📝 <i>{data['description']}</i>\n\n"
        f"💰 Narxi: {data['price']}\n"
        f"📦 Holati: {stock_text}"
    )
    await state.set_state(AdminProductStates.waiting_for_confirmation)
    if data['photos']:
        await message.answer_photo(photo=data['photos'][0], caption=f"Preview:\n\n{text}", parse_mode="HTML", reply_markup=get_product_preview_kb())
    else:
        await message.answer(f"Preview:\n\n{text}", parse_mode="HTML", reply_markup=get_product_preview_kb())

@admin_router.message(AdminProductStates.waiting_for_confirmation)
async def product_confirm(message: Message, state: FSMContext):
    if message.text == "✅ Ha (Saqlash)":
        data = await state.get_data()
        await db.add_product(data['category_id'], data['title'], data['description'], data['price'], data['photos'], data['in_stock'])
        await message.answer("✅ Beshik muvaffaqiyatli saqlandi!", reply_markup=get_admin_main_menu())
    else:
        await message.answer("❌ Bekor qilindi.", reply_markup=get_admin_main_menu())
    await state.clear()


@admin_router.message(F.text == "📦 Mahsulotlar (Tahrir/O'chirish)")
async def manage_products_cats(message: Message):
    if not await is_admin(message.from_user.id): return
    categories = await db.get_all_categories(active_only=True)
    await message.answer("Qaysi kategoriyadagi mahsulotlarni boshqaramiz?", reply_markup=get_admin_products_manage_kb(categories))

@admin_router.callback_query(F.data == "admin_back_to_prod_cats")
async def admin_back_to_prod_cats(callback: CallbackQuery):
    categories = await db.get_all_categories(active_only=True)
    await callback.message.edit_text("Qaysi kategoriyadagi mahsulotlarni boshqaramiz?", reply_markup=get_admin_products_manage_kb(categories))

@admin_router.callback_query(F.data.startswith("admin_prodcat:"))
async def admin_prodcat_selected(callback: CallbackQuery):
    cat_id = int(callback.data.split(":")[1])
    products = await db.get_products_by_category(cat_id, active_only=True, limit=100) # getting max 100 for admin
    await callback.message.edit_text("Mahsulotni tanlang:", reply_markup=get_admin_products_list_kb(products, cat_id))

@admin_router.callback_query(F.data.startswith("admin_del_prod:"))
async def admin_del_prod(callback: CallbackQuery):
    prod_id = int(callback.data.split(":")[1])
    await db.soft_delete_product(prod_id)
    await callback.answer("Mahsulot o'chirildi.")
    await callback.message.delete()

@admin_router.callback_query(F.data.startswith("admin_edit_prod:"))
async def admin_edit_prod_start(callback: CallbackQuery, state: FSMContext):
    prod_id = int(callback.data.split(":")[1])
    await state.update_data(prod_id=prod_id, photos=[])
    await state.set_state(AdminProductEditStates.waiting_for_photos)
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Rasmni o'zgartirmaslik", callback_data="skip_photos")], [InlineKeyboardButton(text="✅ Yangi rasmlarni yukladim", callback_data="done_photos")]])
    await callback.message.answer("YANGI rasmlarni yuboring (Yoki o'zgartirmaslik tugmasini bosing):", reply_markup=kb)
    await callback.answer()

@admin_router.message(AdminProductEditStates.waiting_for_photos, F.photo)
async def admin_edit_photo_recv(message: Message, state: FSMContext):
    async with photo_upload_lock:
        data = await state.get_data()
        photos = data.get('photos', [])
        photos.append(message.photo[-1].file_id)
        await state.update_data(photos=photos)
    await message.reply(f"✅ {len(photos)}-yangi rasm qabul qilindi. Yana yuboring yoki '✅ Yangi rasmlarni yukladim' tugmasini bosing.")

@admin_router.callback_query(AdminProductEditStates.waiting_for_photos, F.data == "skip_photos")
async def admin_edit_skip_photos(callback: CallbackQuery, state: FSMContext):
    await state.update_data(skip_photos=True)
    await state.set_state(AdminProductEditStates.waiting_for_title)
    await callback.message.answer("YANGI nomini kiriting:")
    await callback.answer()

@admin_router.callback_query(AdminProductEditStates.waiting_for_photos, F.data == "done_photos")
async def admin_edit_done_photos(callback: CallbackQuery, state: FSMContext):
    await state.update_data(skip_photos=False)
    await state.set_state(AdminProductEditStates.waiting_for_title)
    await callback.message.answer("YANGI nomini kiriting:")
    await callback.answer()

@admin_router.message(AdminProductEditStates.waiting_for_title)
async def admin_edit_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(AdminProductEditStates.waiting_for_description)
    await message.answer("YANGI izohini kiriting:")

@admin_router.message(AdminProductEditStates.waiting_for_description)
async def admin_edit_desc(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(AdminProductEditStates.waiting_for_price)
    await message.answer("YANGI narxini kiriting:")

@admin_router.message(AdminProductEditStates.waiting_for_price)
async def admin_edit_price(message: Message, state: FSMContext):
    await state.update_data(price=message.text)
    await state.set_state(AdminProductEditStates.waiting_for_stock)
    await message.answer("Mavjudlik holatini tanlang:", reply_markup=get_in_stock_kb())

@admin_router.message(AdminProductEditStates.waiting_for_stock)
async def admin_edit_stock(message: Message, state: FSMContext):
    in_stock = True if message.text == "✅ Mavjud" else False
    data = await state.get_data()
    
    photos = None if data.get('skip_photos') else data.get('photos')
    await db.update_product_all(data['prod_id'], data['title'], data['description'], data['price'], in_stock, photos)
    
    await message.answer("✅ Mahsulot muvaffaqiyatli tahrirlandi!", reply_markup=get_admin_main_menu())
    await state.clear()

# --- Reply to Inquiry ---
@admin_router.callback_query(F.data.startswith("reply:"))
async def reply_to_inquiry_start(callback: CallbackQuery, state: FSMContext):
    _, user_id, inquiry_id = callback.data.split(":")
    await state.update_data(target_user_id=int(user_id), inquiry_id=int(inquiry_id))
    await state.set_state(AdminReplyStates.waiting_for_reply)
    await callback.message.answer(f"Mijozga javob matnini yozing (so'rov #{inquiry_id}):", reply_markup=get_cancel_inline_kb())
    await callback.answer()

@admin_router.message(AdminReplyStates.waiting_for_reply)
async def reply_to_inquiry_send(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    target_user_id = data['target_user_id']
    inquiry_id = data['inquiry_id']
    
    try:
        await bot.send_message(chat_id=target_user_id, text=f"📩 <b>Do'kondan javob:</b>", parse_mode="HTML")
        await message.copy_to(chat_id=target_user_id)
        await db.update_inquiry_status(inquiry_id, 'answered')
        await message.answer("✅ Javob yuborildi.")
    except Exception as e:
        await message.answer("❌ Xatolik: Foydalanuvchiga xabar yuborib bo'lmadi (u botni bloklagan bo'lishi mumkin).")
    finally:
        await state.clear()

@admin_router.message(F.text == "📥 So'rovlar")
async def show_new_inquiries(message: Message):
    if not await is_admin(message.from_user.id): return
    inquiries = await db.get_new_inquiries()
    if not inquiries:
        await message.answer("Yangi so'rovlar yo'q 😌.")
        return
    for inq in inquiries:
        text = f"So'rov #{inq['id']}\nMijoz: {inq['user_name']} (ID: {inq['user_id']})\nXabar: {inq['message_text']}"
        await message.answer(text, reply_markup=get_reply_to_inquiry_kb(inq['user_id'], inq['id']))
