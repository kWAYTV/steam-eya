pyinstaller --onefile --noconsole --icon="%~dp0assets\icon.ico" --name CacheLogin main.py
rmdir /s /q build
del /f /q CacheLogin.spec

if exist assets\icon.ico (echo Icon found) else (echo Icon missing)

