pyinstaller --onefile --noconsole --icon="%~dp0assets\icon.ico" --name steam-eya main.py
rmdir /s /q build
del /f /q steam-eya.spec

if exist assets\icon.ico (echo Icon found) else (echo Icon missing)

