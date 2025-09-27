import argparse
import os
from ShellEmulator import ShellEmulator


def main():
    parser = argparse.ArgumentParser(
        description="Эмулятор командной оболочки ")
    parser.add_argument("--vfs-path",
                        type=str, help="Путь к физическому расположению VFS")
    parser.add_argument("--startup-script", 
                        type=str, help="Путь к стартовому скрипту")

    args = parser.parse_args()

    vfs_name = os.path.basename(args.vfs_path) if args.vfs_path else "VFS"
    emulator = ShellEmulator(vfs_name=vfs_name, 
                             vfs_path=args.vfs_path, 
                             startup_script=args.startup_script)
    emulator.run()


if __name__ == "__main__":
    main()
