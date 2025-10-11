@echo off
chcp 65001 > nul
REM Запуск эмулятора с передачей параметров через командную строку
cd /d "%~dp0\.."

if "%1"=="" (
    echo Использование: run_args.bat [vfs_файл] [startup_скрипт]
    echo Пример: run_args.bat standard_vfs.json
    echo Пример: run_args.bat minimal_vfs.json demo_startup.txt
    pause
    exit /b 1
)

set "VFS_FILE=data\%1"
if not "%2"=="" (
    set "SCRIPT_FILE=scripts\%2"
    echo Запуск Shell Emulator с VFS: %1 и скриптом: %2
    python main.py --vfs-path "%VFS_FILE%" --startup-script "%SCRIPT_FILE%"
) else (
    echo Запуск Shell Emulator с VFS: %1
    python main.py --vfs-path "%VFS_FILE%"
)
pause