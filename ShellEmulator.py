import sys
import shlex
import os
from typing import Optional, List, Tuple, Dict, Callable
from VFS import VFS


class ShellEmulator:
    def __init__(self, vfs_name: str = "VFS", 
                 vfs_path: Optional[str] = None, 
                 startup_script: Optional[str] = None) -> None:
        self.vfs_name: str = vfs_name
        self.vfs_path: Optional[str] = vfs_path
        self.startup_script: Optional[str] = startup_script
        self.current_path: str = "/"
        self.running: bool = True
        self.vfs = VFS(vfs_path)

        self.commands: Dict[str, Callable[[List[str]], None]] = {
            'ls': self.cmd_ls,
            'cd': self.cmd_cd, 
            'exit': self.cmd_exit,
            'clear': lambda args: sys.stdout.write('\033c'),
            'cat': self.cmd_cat,
            'pwd': self.cmd_pwd,
            'touch': self.cmd_touch,
            'mkfile': self.cmd_mkfile,
            'mkdir': self.cmd_mkdir,
            'mv': self.cmd_mv,
            'tree': self.cmd_tree
        }

    def parse_command(self, input_line: str) -> Tuple[Optional[str], List[str]]:
        """Парсер команд - разделяет ввод на команду и аргументы"""
        input_line = input_line.strip()

        if not input_line:
            return None, []

        try:
            parts = shlex.split(input_line) # Разделение с учетом кавычек
        except ValueError as e:
            print(f"Ошибка парсинга команды: {e}")
            return None, []

        if not parts:
            return None, []

        command = parts[0]
        args = parts[1:] if len(parts) > 1 else []

        return command, args

    def get_prompt(self) -> str:
        return f"{self.vfs_name}:{self.current_path}$ "

    def cmd_ls(self, args: List[str]) -> None:
        path = self.current_path
        if args:
            path = self.vfs.normalize_path(self.current_path, args[0])

        if not self.vfs.exists(path):
            print(f"ls: {args[0] if args else '.'}: Нет такого файла или каталога")
            return

        if self.vfs.is_file(path):
            print(os.path.basename(path))
        else:
            items = self.vfs.list_directory(path)
            for item in sorted(items):
                item_path = f"{path}/{item}" if path != "/" else f"/{item}"
                if self.vfs.is_directory(item_path):
                    print('-', f"{item}/")
                else:
                    print('-', item)

    def cmd_cd(self, args: List[str]) -> None:
        if not args:
            self.current_path = "/"
            return

        target_path = self.vfs.normalize_path(self.current_path, args[0])

        if not self.vfs.exists(target_path):
            print(f"cd: {args[0]}: Нет такого файла или каталога")
            return

        if not self.vfs.is_directory(target_path):
            print(f"cd: {args[0]}: Это не каталог")
            return
        
        self.current_path = target_path

    def cmd_cat(self, args: List[str]) -> None:
        """ Выводит содержимое файла
        """
        if not args:
            print("cat: отсутствует операнд")
            return
        
        for filename in args:
            file_path = self.vfs.normalize_path(self.current_path, filename)
            
            if not self.vfs.exists(file_path):
                print(f"cat: {filename}: Нет такого файла или каталога")
                continue
            
            if self.vfs.is_directory(file_path):
                print(f"cat: {filename}: Это каталог")
                continue
            
            content = self.vfs.read_file(file_path)
            if content is not None:
                print(content)
            else:
                print(f"cat: {filename}: Ошибка чтения файла")

    def cmd_touch(self, args: List[str]) -> None:
        """ Создает пустой файл
        """
        if not args:
            print("touch: отсутствует операнд")
            return

        for filename in args:
            file_path = self.vfs.normalize_path(self.current_path, filename)

            if self.vfs.exists(file_path):
                if self.vfs.is_directory(file_path):
                    print(f"touch: {filename}: Это каталог")
                continue

            success = self.vfs.create_file(file_path, "")
            if not success:
                print(f"touch: {filename}: Ошибка создания файла")
    
    def cmd_mkfile(self, args: List[str]) -> None:
        """ Создает файл с указанным содержимым
        """
        if len(args) < 2:
            print("mkfile: требуется имя файла и содержимое")
            return

        filename = args[0]
        content = ' '.join(args[1:])
        file_path = self.vfs.normalize_path(self.current_path, filename)

        if self.vfs.exists(file_path):
            print(f"mkfile: {filename}: Файл уже существует")
            return

        success = self.vfs.create_file(file_path, content)
        if not success:
            print(f"mkfile: {filename}: Ошибка создания файла")

    def cmd_mkdir(self, args: List[str]) -> None:
        """ Создает каталог
        """
        if not args:
            print("mkdir: отсутствует операнд")
            return

        for dirname in args:
            dir_path = self.vfs.normalize_path(self.current_path, dirname)

            if self.vfs.exists(dir_path):
                print(f"mkdir: {dirname}: Каталог уже существует")
                continue

            success = self.vfs.create_directory(dir_path)
            if not success:
                print(f"mkdir: {dirname}: Ошибка создания каталога")

    def cmd_mv(self, args: List[str]) -> None:
        """ Перемещает или переименовывает файл/каталог
        """
        if len(args) < 2:
            print("mv: требуется источник и назначение")
            return

        source = args[0]
        destination = args[1]
        
        source_path = self.vfs.normalize_path(self.current_path, source)
        dest_path = self.vfs.normalize_path(self.current_path, destination)

        # Проверяем существование источника
        if not self.vfs.exists(source_path):
            print(f"mv: {source}: Нет такого файла или каталога")
            return

        # Проверяем, не пытаемся ли переместить в себя
        if source_path == dest_path:
            print(f"mv: {source} и {destination} одинаковы")
            return

        # Получаем данные источника
        source_node = self.vfs.get_node(source_path)
        if source_node is None:
            print(f"mv: {source}: Ошибка получения данных")
            return

        # Если назначение существует и это каталог, перемещаем внутрь него
        if self.vfs.exists(dest_path) and self.vfs.is_directory(dest_path):
            source_name = os.path.basename(source_path)
            dest_path = f"{dest_path}/{source_name}" if dest_path != "/" else f"/{source_name}"

        # Проверяем, не существует ли уже файл назначения
        if self.vfs.exists(dest_path):
            print(f"mv: {destination}: Файл или каталог уже существует")
            return

        # Создаем в новом месте
        success = False
        if self.vfs.is_file(source_path):
            content = self.vfs.read_file(source_path)
            if content is not None:
                success = self.vfs.create_file(dest_path, content)
        else:
            success = self.vfs.move_directory(source_path, dest_path)

        if success:
            # Удаляем из старого места
            self.vfs.remove_node(source_path)
        else:
            print(f"mv: Ошибка перемещения {source} в {destination}")

    def cmd_tree(self, args: List[str]) -> None:
        """ Отображает структуру каталогов в виде дерева
        """
        start_path = self.current_path
        if args:
            start_path = self.vfs.normalize_path(self.current_path, args[0])

        if not self.vfs.exists(start_path):
            print(f"tree: {args[0] if args else '.'}: Нет такого файла или каталога")
            return

        if not self.vfs.is_directory(start_path):
            print(f"tree: {args[0] if args else '.'}: Это не каталог")
            return

        print(start_path if start_path != "/" else "/")
        self._print_tree(start_path, "", True)

    def _print_tree(self, path: str, prefix: str, is_last: bool) -> None:
        """ Вспомогательный метод для рекурсивного отображения дерева
        """
        items = self.vfs.list_directory(path)
        items.sort()

        for i, item in enumerate(items):
            is_last_item = (i == len(items) - 1)
            item_path = f"{path}/{item}" if path != "/" else f"/{item}"
            
            # Символы для отображения дерева
            connector = "└── " if is_last_item else "├── "
            print(f"{prefix}{connector}{item}{'/' if self.vfs.is_directory(item_path) else ''}")
            
            # Рекурсивно обрабатываем подкаталоги
            if self.vfs.is_directory(item_path):
                extension = "    " if is_last_item else "│   "
                self._print_tree(item_path, prefix + extension, is_last_item)

    def cmd_pwd(self, args: List[str]) -> None:
        print(self.current_path)

    def cmd_exit(self, args: List[str]) -> None:
        print("Выход из эмулятора...")
        self.running = False

    def execute_startup_script(self) -> None:
        """Выполняет стартовый скрипт, если он задан"""
        if not self.startup_script or not os.path.exists(self.startup_script):
            return

        try:
            with open(self.startup_script, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            for _, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                print(f"{self.get_prompt()}{line}")

                command, args = self.parse_command(line)
                if command:
                    self.execute_command(command, args)

        except FileNotFoundError:
            print(f"Ошибка: файл стартового скрипта '{self.startup_script}' не найден")
        except Exception as e:
            print(f"Ошибка при выполнении стартового скрипта: {e}")

    def execute_command(self, command: str, args: List[str]) -> None:
        if command in self.commands:
            try:
                self.commands[command](args)
            except Exception as e:
                print(f"Ошибка выполнения команды '{command}': {e}")
        else:
            print(f"Команда '{command}' не найдена")

    def run(self) -> None:
        """Основной цикл"""
        print(f"Эмулятор командной оболочки запущен!")
        print(f"Виртуальная файловая система: {self.vfs_name}")
        if self.vfs_path:
            print(f"Путь к VFS: {self.vfs_path}")
        print("Доступные команды: ls, cd, cat, pwd, touch, mkfile, mkdir, mv, tree, clear, exit")
        print("Для выхода введите 'exit'")
        print()

        # Выполняем стартовый скрипт, если он есть
        if self.startup_script:
            self.execute_startup_script()

        while self.running:
            try:
                user_input = input(self.get_prompt())
                command, args = self.parse_command(user_input)

                if command:
                    self.execute_command(command, args)

            except KeyboardInterrupt:
                print("\nПрерывание работы...")
                break

            except EOFError:
                print("\nЗавершение работы...")
                break

            except Exception as e:
                print(f"Неожиданная ошибка: {e}")
