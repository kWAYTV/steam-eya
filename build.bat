pyinstaller --onefile --noconsole --icon=assets/icon.ico --name CacheLogin main.py
rmdir /s /q build
del /f /q CacheLogin.spec
