@echo off
chcp 65001 > nul
REM Интерактивный выбор параметров запуска
cd /d "%~dp0\.."

echo ========================================
echo     ИНТЕРАКТИВНЫЙ ЗАПУСК ЭМУЛЯТОРА
echo ========================================
echo.

REM Показываем доступные VFS файлы
echo Доступные VFS файлы:
if exist "data" (
    for %%f in ("data\*.json") do (
        echo - %%~nxf
    )
) else (
    echo Нет доступных VFS файлов.
)
echo.

set /p vfs_choice="Введите имя VFS файла (с .json) или нажмите Enter для standard_vfs.json: "
if "%vfs_choice%"=="" set "vfs_choice=standard_vfs.json"

echo.
echo Хотите использовать startup скрипт? (y/N)
set /p use_script=""

if /i "%use_script%"=="y" (
    echo.
    echo Доступные startup скрипты:
    if exist "scripts" (
        for %%f in ("scripts\*.txt") do (
            echo - %%~nxf
        )
    ) else (
        echo Нет доступных скриптов.
    )
    echo.
    set /p script_choice="Введите имя скрипта (с .txt): "
    
    if not "%script_choice%"=="" (
        echo.
        echo Запуск с VFS: %vfs_choice% и скриптом: %script_choice%
        python main.py --vfs-path "data\%vfs_choice%" --startup-script "scripts\%script_choice%"
    ) else (
        echo.
        echo Запуск с VFS: %vfs_choice% (без скрипта)
        python main.py --vfs-path "data\%vfs_choice%"
    )
) else (
    echo.
    echo Запуск с VFS: %vfs_choice%
    python main.py --vfs-path "data\%vfs_choice%"
)

pause