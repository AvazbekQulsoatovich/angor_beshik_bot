import sys

def process(filepath, mappings):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for old, new in mappings.items():
        content = content.replace(old, new)
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Processed {filepath}')

finance_maps = {
    'F.text == "🛒 Sotuv qilish"': 'F.text.in_({"🛒 Sotuv qilish", "📥 Kirim (Sotuv)"})',
    'F.text == "📦 Omborga tovar qo\'shish"': 'F.text.in_({"📦 Omborga tovar qo\'shish", "📥 Omborga kirim"})',
    'F.text == "💸 Boshqa xarajatlar"': 'F.text.in_({"💸 Boshqa xarajatlar", "📤 Boshqa xarajatlar", "📤 Chiqim (Xarajat)"})',
    'F.text == "📊 Moliya va Hisobot"': 'F.text.in_({"📊 Moliya va Hisobot", "💰 Moliya va Statistika"})',
}

admin_maps = {
    'F.text == "✏️ Tovarlarni o\'zgartirish"': 'F.text.in_({"✏️ Tovarlarni o\'zgartirish", "📦 Mahsulotlar (Tahrir)", "📦 Mahsulotlar (Tahrir/O\'chirish)"})',
    'F.text == "📂 Bo\'limlar"': 'F.text.in_({"📂 Bo\'limlar", "📂 Kategoriyalar"})',
    'F.text == "📩 Xabarlar"': 'F.text.in_({"📩 Xabarlar", "📥 So\'rovlar"})',
    'F.text == "👥 Admin qo\'shish"': 'F.text.in_({"👥 Admin qo\'shish", "👥 Adminlar", "👥 Adminlarni boshqarish"})',
    'F.text == "➕ Yangi mahsulot"': 'F.text.in_({"➕ Yangi mahsulot", "➕ Mahsulot qo\'shish"})'
}

process('c:/Users/Avaz/Desktop/beshikbot/handlers/finance.py', finance_maps)
process('c:/Users/Avaz/Desktop/beshikbot/handlers/admin.py', admin_maps)
