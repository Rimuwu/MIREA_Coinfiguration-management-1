@echo off
chcp 65001 > nul
REM Простой запуск эмулятора с минимальным VFS
cd /d "%~dp0\.."
echo Запуск Shell Emulator с минимальным VFS...
python main.py --vfs-path "data\minimal_vfs.json"
pause