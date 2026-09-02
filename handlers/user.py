from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from config import ADMIN_IDS
import json

from keyboards.user_kb import get_main_menu, get_categories_kb, get_product_pagination_kb, get_cancel_inline_kb
from database import db
from states.user_states import UserStates

user_router = Router()

async def get_all_admins():
    db_admins = await db.get_all_admins()
    return list(set(ADMIN_IDS + db_admins))

async def is_admin(user_id):
    admins = await get_all_admins()
    return user_id in admins

@user_router.message(F.text == "/start", StateFilter('*'))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    is_adm = await is_admin(message.from_user.id)
    text = (
        "🌟 **Assalomu alaykum! Angor Beshiklari do'koniga xush kelibsiz!** 👶✨\n\n"
        "Farzandingiz uchun eng sifatli, xavfsiz va chiroyli beshiklarni aynan shu yerdan topishingiz mumkin.\n\n"
        "👇 Iltimos, quyidagi menyudan kerakli bo'limni tanlang:"
    )
    await message.answer(text, reply_markup=get_main_menu(is_adm), parse_mode="Markdown")

@user_router.message(F.text == "ℹ️ Biz haqimizda", StateFilter('*'))
async def show_address(message: Message):
    text = (
        "📍 **Bizning manzil:** Angor bozori.\n\n"
        "⏰ **Ish vaqti:** Har kuni 08:00 dan 18:00 gacha.\n\n"
        "📞 **Admin (Telegram):** @jasurbekkk01\n"
        "📱 **Telefon:** +998 95 777 51 95\n\n"
        "📸 **Instagram:** [@angor_beshiklari](https://instagram.com/angor_beshiklari)\n\n"
        "Xaridingiz uchun oldindan rahmat! 🛍"
    )
    # Telegramning original lokatsiyasini yuborish (Xarita kartochkasi)
    await message.answer_venue(latitude=37.4460347, longitude=67.1538179, title="Angor Beshiklari do'koni", address="Angor bozori")
    await message.answer(text, parse_mode="Markdown")

@user_router.message(F.text == "👨‍💻 Admin bilan aloqa", StateFilter('*'))
async def contact_admin_general(message: Message):
    text = (
        "Sotuvchiga to'g'ridan to'g'ri yozish uchun @jasurbekkk01 ga murojaat qiling yoki +998 95 777 51 95 raqamiga qo'ng'iroq qiling.\n\n"
        "📸 **Instagram:** [@angor_beshiklari](https://instagram.com/angor_beshiklari)\n"
    )
    await message.answer(text, parse_mode="Markdown")

@user_router.message(F.text == "🛍 Katalog", StateFilter('*'))
async def show_catalog(message: Message):
    categories = await db.get_all_categories(active_only=True)
    if not categories:
        await message.answer("Hozircha kategoriyalar mavjud emas 😔.")
        return
    await message.answer("Qaysi turdagi beshiklar sizni qiziqtiradi? 👇", reply_markup=get_categories_kb(categories))

@user_router.callback_query(F.data == "back_to_cats")
async def back_to_cats(callback: CallbackQuery):
    categories = await db.get_all_categories(active_only=True)
    try:
        await callback.message.delete()
    except:
        pass
    await callback.message.answer("Qaysi turdagi beshiklar sizni qiziqtiradi? 👇", reply_markup=get_categories_kb(categories))

@user_router.callback_query(F.data.startswith("cat:"))
async def category_selected(callback: CallbackQuery):
    category_id = int(callback.data.split(":")[1])
    await show_product_page(callback, category_id, 1)

@user_router.callback_query(F.data.startswith("prod:"))
async def product_pagination(callback: CallbackQuery):
    _, category_id, page = callback.data.split(":")
    await show_product_page(callback, int(category_id), int(page))

async def show_product_page(callback: CallbackQuery, category_id: int, page: int):
    limit = 1
    total_products = await db.get_products_count_by_category(category_id)
    if total_products == 0:
        await callback.answer("Bu kategoriyada hozircha mahsulot yo'q", show_alert=True)
        return
    
    total_pages = total_products
    if page < 1: page = 1
    if page > total_pages: page = total_pages
    
    products = await db.get_products_by_category(category_id, page=page, limit=1)
    if not products:
        await callback.answer("Mahsulot topilmadi", show_alert=True)
        return
    
    product = products[0]
    stock_text = "✅ Sotuvda mavjud" if product['in_stock'] else "⏳ Buyurtma asosida yasaladi"
    text = (
        f"🏷 <b>{product['title']}</b>\n\n"
        f"📝 <i>{product['description']}</i>\n\n"
        f"💰 <b>Narxi:</b> {product['price']}\n"
        f"📦 <b>Holati:</b> {stock_text}"
    )
    
    kb = get_product_pagination_kb(category_id, product['id'], page, total_pages)
    
    photo_ids = json.loads(product['photo_file_ids'])
    
    try:
        await callback.message.delete()
    except:
        pass
        
    if len(photo_ids) > 0:
        main_photo = photo_ids[0]
        await callback.message.answer_photo(photo=main_photo, caption=text, reply_markup=kb, parse_mode="HTML")
    else:
        await callback.message.answer(text, reply_markup=kb, parse_mode="HTML")
    
    await callback.answer()

@user_router.callback_query(F.data.startswith("contact:"))
async def contact_admin(callback: CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split(":")[1])
    product = await db.get_product_by_id(product_id)
    if not product:
        await callback.answer("Xatolik: Mahsulot topilmadi.", show_alert=True)
        return
    
    await state.update_data(product_id=product_id)
    await state.set_state(UserStates.waiting_for_message)
    
    text = f"✍️ <b>{product['title']}</b> haqida savolingiz yoki buyurtmangizni yozing.\n(Masalan: qaysi ranglari bor, dastavka qachon bo'ladi, va hokazo):"
    await callback.message.answer(text, parse_mode="HTML", reply_markup=get_cancel_inline_kb())
    await callback.answer()

@user_router.callback_query(F.data == "cancel_action")
async def cancel_action(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await callback.message.delete()
    except:
        pass
    await callback.message.answer("❌ Amal bekor qilindi.")

@user_router.message(UserStates.waiting_for_message)
async def process_inquiry_message(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    product_id = data.get("product_id")
    product = await db.get_product_by_id(product_id)
    
    msg_text = message.text or message.caption or "[Media / Fayl / Lokatsiya]"
    inquiry_id = await db.add_inquiry(product_id, message.from_user.id, message.from_user.full_name, msg_text)
    
    admin_text = (
        f"🆕 <b>Yangi so'rov!</b>\n"
        f"👤 Mijoz: {message.from_user.full_name} (@{message.from_user.username or 'yoq'}, ID: <code>{message.from_user.id}</code>)\n"
        f"🛏️ Beshik: {product['title']} — {product['price']}"
    )
    
    from keyboards.admin_kb import get_reply_to_inquiry_kb
    admins = await get_all_admins()
    for admin_id in admins:
        try:
            await bot.send_message(chat_id=admin_id, text=admin_text, parse_mode="HTML")
            await message.copy_to(chat_id=admin_id, reply_markup=get_reply_to_inquiry_kb(message.from_user.id, inquiry_id))
        except Exception as e:
            pass
            
    await state.clear()
    await message.answer("✅ Xabaringiz sotuvchiga yuborildi. Tez orada sizga shu yerning o'zida javob yozishadi. Iltimos kuting.")

@user_router.message(StateFilter("*"))
async def global_fallback(message: Message):
    await message.reply("⚠️ Noma'lum buyruq yoki amal. Iltimos, pastdagi menyudan foydalaning 👇")
