@echo off
chcp 65001 > nul
REM Создание и запуск с пустым VFS
cd /d "%~dp0\.."
echo Создание пустого VFS для экспериментов...

REM Создаем абсолютно пустой VFS
echo {}> "data\empty_vfs.json"

echo Запуск Shell Emulator с пустым VFS...
echo Используйте команды mkdir и mkfile для создания структуры.
python main.py --vfs-path "data\empty_vfs.json"
pause