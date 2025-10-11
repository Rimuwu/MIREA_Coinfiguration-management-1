@echo off
chcp 65001 > nul
REM Запуск эмулятора с пользовательским VFS
cd /d "%~dp0\.."
set /p vfs_name="Введите имя VFS файла (без .json): "
if "%vfs_name%"=="" (
    echo Имя файла не может быть пустым!
    pause
    exit /b 1
)
echo Запуск Shell Emulator с VFS: %vfs_name%.json
python main.py --vfs-path "data\%vfs_name%.json"
pause