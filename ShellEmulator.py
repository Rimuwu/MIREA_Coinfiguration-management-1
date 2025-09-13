import sys
import shlex
from typing import Optional, List, Tuple, Dict, Callable


class ShellEmulator:
    """Эмулятор командной оболочки"""

    def __init__(self, vfs_name: str = "VFS") -> None:
        self.vfs_name: str = vfs_name
        self.current_path: str = "/"
        self.running: bool = True

        self.commands: Dict[str, Callable[[List[str]], None]] = {
            'ls': self.cmd_ls,
            'cd': self.cmd_cd, 
            'exit': self.cmd_exit,
            'clear': lambda args: sys.stdout.write('\033c'),
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
        """Команда-заглушка ls"""
        print(f"Команда: ls")
        if args:
            print(f"Аргументы: {' '.join(args)}")
        else:
            print("Аргументы: отсутствуют")

    def cmd_cd(self, args: List[str]) -> None:
        """Команда-заглушка cd"""
        print(f"Команда: cd")
        if args:
            print(f"Аргументы: {' '.join(args)}")
        else:
            print("Аргументы: отсутствуют")

    def cmd_exit(self, args: List[str]) -> None:
        """Команда выхода из эмулятора"""
        print("Выход из эмулятора...")
        self.running = False

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
        print("Доступные команды: ls, cd, exit")
        print("Для выхода введите 'exit'")
        print()

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
