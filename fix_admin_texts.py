import sys

with open('c:/Users/Avaz/Desktop/beshikbot/handlers/admin.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('F.text == "📦 Mahsulotlar (Tahrir)"', 'F.text == "✏️ Tovarlarni o\'zgartirish"')
content = content.replace('F.text == "📂 Kategoriyalar"', 'F.text == "📂 Bo\'limlar"')
content = content.replace('F.text == "📥 So\'rovlar"', 'F.text == "📩 Xabarlar"')
content = content.replace('F.text == "👥 Adminlarni boshqarish"', 'F.text == "👥 Admin qo\'shish"')
content = content.replace('F.text == "👥 Adminlar"', 'F.text == "👥 Admin qo\'shish"')

with open('c:/Users/Avaz/Desktop/beshikbot/handlers/admin.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Replaced admin.py')
