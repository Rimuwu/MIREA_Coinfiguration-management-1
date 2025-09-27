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
            'mkdir': self.cmd_mkdir
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
        print("Доступные команды: ls, cd, cat, pwd, exit, clear")
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
