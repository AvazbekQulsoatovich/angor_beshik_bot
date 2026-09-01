import re

def add_state_filter(filepath, targets):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Ensure StateFilter is imported
    if 'StateFilter' not in content:
        content = content.replace('from aiogram.filters import Command', 'from aiogram.filters import Command, StateFilter')
        if 'StateFilter' not in content:
            content = content.replace('from aiogram import Router', 'from aiogram import Router\nfrom aiogram.filters import StateFilter')
    
    # Replace targets
    for target in targets:
        # Search for exact decorator match
        pattern = r"(@[a-z_]+\.message\(" + re.escape(target) + r"\))"
        replacement = r"@\g<1>".replace(target + ")", target + ", StateFilter('*'))")
        
        # We can also do a simpler string replace since we know the exact strings
        search_str = f"@user_router.message({target})"
        replace_str = f"@user_router.message({target}, StateFilter('*'))"
        content = content.replace(search_str, replace_str)
        
        search_str2 = f"@admin_router.message({target})"
        replace_str2 = f"@admin_router.message({target}, StateFilter('*'))"
        content = content.replace(search_str2, replace_str2)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

user_targets = [
    'F.text == "ℹ️ Biz haqimizda"',
    'F.text == "👨‍💻 Admin bilan aloqa"',
    'F.text == "🛍 Katalog"',
]
add_state_filter('handlers/user.py', user_targets)

admin_targets = [
    'Command("admin")',
    'F.text == "🛠 Admin Panel"',
    'F.text == "🏠 Asosiy menyu"',
    'F.text == "👥 Adminlarni boshqarish"',
    'F.text == "📂 Kategoriyalar"',
    'F.text == "➕ Mahsulot qo\'shish"',
    'F.text == "📦 Mahsulotlar (Tahrir/O\'chirish)"',
    'F.text == "📥 So\'rovlar"'
]
add_state_filter('handlers/admin.py', admin_targets)

# Also fix the global fallback
with open('handlers/user.py', 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace('@user_router.message()', '@user_router.message(StateFilter("*"))')
with open('handlers/user.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Patch applied.")
