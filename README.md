# Эмулятор командной оболочки (Shell Emulator)

Простой эмулятор командной оболочки для работы с виртуальной файловой системой.

## <kbd>🍕</kbd> Описание

Программа представляет собой эмулятор оболочки Unix-подобной системы, который работает с виртуальной файловой системой (VFS), хранящейся в JSON файле. Позволяет выполнять базовые команды для навигации и работы с файлами.

## <kbd>⚡</kbd> Файлы проекта

- `main.py` - точка входа в программу
- `ShellEmulator.py` - основная логика эмулятора оболочки
- `VFS.py` - класс для работы с виртуальной файловой системой
- `data/` - папка с готовыми конфигурациями VFS
- `scripts/` - готовые скрипты для демонстрации
- `bat-scipts/` - batch файлы для запуска

## <kbd>🕹️</kbd> Поддерживаемые команды

- `ls` - список файлов и папок
- `cd` - смена директории
- `pwd` - показать текущую директорию
- `cat` - просмотр содержимого файла
- `touch` - создание пустого файла
- `mkfile` - создание файла с содержимым
- `mkdir` - создание директории
- `mv` - перемещение/переименование
- `tree` - отображение структуры директорий
- `clear` - очистка экрана
- `exit` - выход из программы

## <kbd>🍕</kbd> Запуск

### Обычный запуск:
```
python main.py
```

### <kbd>❤️</kbd> С параметрами:
```
python main.py --vfs-path data/standard_vfs.json --startup-script scripts/startup_script1
```

### <kbd>🦕</kbd> Готовые bat файлы:
- `run_interactive.bat` - интерактивный запуск
- `run_empty.bat` - запуск с пустой VFS
- `run_minimal.bat` - запуск с минимальной VFS

## <kbd>⚙️</kbd> Структура VFS

Виртуальная файловая система хранится в JSON формате. Директории представлены как объекты, файлы как строки.

## <kbd>🍕</kbd> Пример вывода в консоль
```
Запуск Shell Emulator с минимальным VFS...
Эмулятор командной оболочки запущен!
Виртуальная файловая система: minimal_vfs.json
Путь к VFS: data\minimal_vfs.json
Доступные команды: ls, cd, cat, pwd, touch, mkfile, mkdir, mv, tree, clear, exit
Для выхода введите 'exit'

minimal_vfs.json:/$ tree
/
└── home/
    └── user/
        └── document.txt
minimal_vfs.json:/$ cd home     
minimal_vfs.json:/home$ mkdir www
minimal_vfs.json:/home$ ls
- user/
- www/
minimal_vfs.json:/home$ cd ..
minimal_vfs.json:/$ tree
/
└── home/
    ├── user/
    │   └── document.txt
    └── www/
minimal_vfs.json:/$ cd home/user
minimal_vfs.json:/home/user$ ls
- document.txt
minimal_vfs.json:/home/user$ mv 
mv: требуется источник и назначение
minimal_vfs.json:/home/user$ mv document.txt ..
minimal_vfs.json:/home/user$ ls
minimal_vfs.json:/home/user$ cd ..
minimal_vfs.json:/home$ ls
- document.txt
- user/
- www/
minimal_vfs.json:/home$
```