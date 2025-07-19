import argostranslate.package

argostranslate.package.update_package_index()
packages = argostranslate.package.get_available_packages()

pairs = [("ru", "en"), ("en", "ru")]

for from_code, to_code in pairs:
    print(f"📦 Установка: {from_code} → {to_code}")
    pkg = next((p for p in packages if p.from_code == from_code and p.to_code == to_code), None)
    if pkg:
        argostranslate.package.install_from_path(pkg.download())
    else:
        print(f"⚠️ Не найдена пара: {from_code} → {to_code}")
