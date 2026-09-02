import sys

with open('c:/Users/Avaz/Desktop/beshikbot/handlers/finance.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace report text
old_report = '''    text = (
        "📊 <b>MOLIYAVIY HISOBOT</b>\\n\\n"
        "━━━ 💹 UMUMIY HISOB ━━━\\n"
        f"💵 Umumiy tushum (Kirim): <b>{stats['total_income']:,} so'm</b>\\n"
        f"💸 Operatsion xarajat (Chiqim): <b>{stats['total_expense']:,} so'm</b>\\n"
        f"📦 Omborga sarmoya (Tovar olishga): <b>{stats['total_restock']:,} so'm</b>\\n"
        f"💰 Sof foyda: <b>{stats['net_profit']:,} so'm</b>\\n\\n"
        
        "━━━ 📅 BUGUNGI KUNLIK HISOB ━━━\\n"
        f"📥 Bugungi kirim (Savdo): <b>{stats['daily_income']:,} so'm</b>\\n"
        f"📤 Bugungi operatsion xarajat: <b>{stats['daily_expense']:,} so'm</b>\\n"
        f"📦 Bugungi tovar olishga sarmoya: <b>{stats['daily_restock']:,} so'm</b>\\n"
    )
    
    if stats['daily_expenses_list']:
        text += "\\n🧾 <i>Bugungi operatsion chiqimlar ro'yxati:</i>\\n"
        for exp in stats['daily_expenses_list']:
            text += f"➖ {exp['description']}: {exp['amount']:,} so'm\\n"
            
    text += (
        "\\n💰 <b>SIZNING CHO'NTAGINGIZDA (Bugun):</b>\\n"
        f"Savdodan tushgan sof foyda (tannarxsiz): <b>{stats['daily_sale_profit']:,} so'm</b>\\n"
        f"Shundan operatsion xarajatlar (taksi, obet) ayrilsa: <b>-{stats['daily_expense']:,} so'm</b>\\n"
        f"👉 <b>Sizga qoldi: {stats['daily_pocket']:,} so'm</b>\\n"
        f"<i>(Izoh: Omborga kiritilgan sarmoya foydadan ayirilmaydi, chunki u omborda tovar bo'lib turibdi)</i>\\n"
    )
    
    text += (
        "\\n━━━ 📦 OMBOR TAHLILI ━━━\\n"
        f"🏷 Mahsulot turi: <b>{inv['total_products']} xil</b>\\n"
        f"📦 Jami dona: <b>{inv['total_qty']} dona</b>\\n"
        f"💸 Tikkan mablag' (tannarx): <b>{inv['total_cost_invested']:,} so'm</b>\\n"
        f"💵 Hammasi sotilsa: <b>{inv['total_potential_revenue']:,} so'm</b>\\n"
        f"📈 Kutilayotgan foyda: <b>{inv['potential_profit']:,} so'm</b>\\n\\n"
    )'''

new_report = '''    text = (
        "📊 <b>MOLIYA VA HISOBOT</b>\\n\\n"
        "━━━ 💹 UMUMIY BIZNES HOLATI ━━━\\n"
        f"💵 Jami sotuvdan tushgan pul: <b>{stats['total_income']:,} so'm</b>\\n"
        f"💸 Jami xarajatlar: <b>{stats['total_expense']:,} so'm</b>\\n"
        f"📦 Tovar olib kelishga ketgan pul: <b>{stats['total_restock']:,} so'm</b>\\n"
        f"💰 Sof foyda: <b>{stats['net_profit']:,} so'm</b>\\n\\n"
        
        "━━━ 📅 BUGUNGI KUNLIK HISOB ━━━\\n"
        f"📥 Bugungi savdo tushumi: <b>{stats['daily_income']:,} so'm</b>\\n"
        f"📤 Bugungi kundalik xarajatlar: <b>{stats['daily_expense']:,} so'm</b>\\n"
        f"📦 Bugun tovar olishga ketgan pul: <b>{stats['daily_restock']:,} so'm</b>\\n"
    )
    
    if stats['daily_expenses_list']:
        text += "\\n🧾 <i>Bugungi xarajatlar ro'yxati:</i>\\n"
        for exp in stats['daily_expenses_list']:
            text += f"➖ {exp['description']}: {exp['amount']:,} so'm\\n"
            
    text += (
        "\\n💰 <b>TOZA FOYDA (Faqat bugun uchun):</b>\\n"
        f"Bugungi savdodan ko'rilgan foyda (tovar puli chiqib ketganda): <b>{stats['daily_sale_profit']:,} so'm</b>\\n"
        f"Shundan bugungi xarajatlar (taksi, obet va h.k) ayrilsa: <b>-{stats['daily_expense']:,} so'm</b>\\n"
        f"👉 <b>Cho'ntakka qolgani (Sizga qoldi): {stats['daily_pocket']:,} so'm</b>\\n"
        f"<i>(Izoh: Yangi tovar olishga ketgan pul xarajatga kirmaydi, chunki u omboringizda turibdi)</i>\\n"
    )
    
    text += (
        "\\n━━━ 📦 OMBORDAGI HOLAT ━━━\\n"
        f"🏷 Necha xil tovar bor: <b>{inv['total_products']} xil</b>\\n"
        f"📦 Jami tovarlar soni: <b>{inv['total_qty']} dona</b>\\n"
        f"💸 Ombordagi tovarlar qiymati (Olingan narxida): <b>{inv['total_cost_invested']:,} so'm</b>\\n"
        f"💵 Hammasi sotilsa bo'ladigan pul: <b>{inv['total_potential_revenue']:,} so'm</b>\\n"
        f"📈 Kutilayotgan toza foyda: <b>{inv['potential_profit']:,} so'm</b>\\n\\n"
    )'''

content = content.replace(old_report, new_report)

# Other small text replacements
content = content.replace('F.text == "💰 Moliya va Statistika"', 'F.text == "📊 Moliya va Hisobot"')
content = content.replace('Qaysi mahsulotdan keldi? Tanlang:', 'Qaysi tovardan olib keldingiz? Tanlang:')
content = content.replace('Bu safar qanchadan (tannarxi) keldi? Faqat raqamda yozing (Masalan: 400000):', 'Tovarni o\'zingiz qanchadan sotib oldingiz? (Masalan: 400000):')
content = content.replace('Mijozlarga qanchadan sotamiz (sotish narxi)? (Masalan: 800000):', 'Xaridorga qanchadan sotamiz? (Masalan: 800000):')
content = content.replace('Nechta dona keldi? (Masalan: 10):', 'Nechta dona olib keldingiz? (Masalan: 10):')
content = content.replace('Chiqim (xarajat) summasini raqamda kiriting (Masalan: 50000):', 'Qancha xarajat qildingiz? Faqat raqam yozing (Masalan: 50000):')
content = content.replace('Nimaga xarajat qilinganini yozing (Masalan: Svet, obyet):', 'Bu pul nimaga ishlatildi? (Masalan: Tushlikka, Taksiga, Svetga):')

with open('c:/Users/Avaz/Desktop/beshikbot/handlers/finance.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Replaced finance.py')
