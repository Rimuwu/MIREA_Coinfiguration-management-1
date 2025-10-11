import json
import base64
import os
from typing import Dict, Any, Optional, List

STANDART_VFS_PATH = 'data/standard_vfs.json'

class VFS:
    def __init__(self, vfs_path: Optional[str] = None):
        self.data: Dict[str, Any] = {}
        self.vfs_path = vfs_path
        if vfs_path and os.path.exists(vfs_path):
            self.load_from_file(vfs_path)
        else:
            self.load_from_file(STANDART_VFS_PATH)

    def load_from_file(self, path: str) -> None:
        with open(path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

    def save_to_file(self, path: str) -> None:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def get_node(self, path: str) -> Optional[Dict[str, Any]]:
        path_parts = [p for p in path.split('/') if p]
        current = self.data

        for part in path_parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        return current

    def list_directory(self, path: str) -> List[str]:
        node = self.get_node(path)
        if isinstance(node, dict):
            return list(node.keys())
        return []

    def is_directory(self, path: str) -> bool:
        node = self.get_node(path)
        return isinstance(node, dict)

    def is_file(self, path: str) -> bool:
        node = self.get_node(path)
        return isinstance(node, str)

    def read_file(self, path: str) -> Optional[str]:
        node = self.get_node(path)
        if isinstance(node, str):
            try:
                return base64.b64decode(node).decode('utf-8')
            except:
                return node
        return None

    def create_file(self, path: str, content: str) -> bool:
        path_parts = [p for p in path.split('/') if p]
        if not path_parts:
            return False

        *dirs, filename = path_parts
        current = self.data

        for part in dirs:
            if part not in current or not isinstance(current[part], dict):
                current[part] = {}
            current = current[part]

        if filename in current:
            return False

        current[filename] = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        return True

    def create_directory(self, path: str) -> bool:
        path_parts = [p for p in path.split('/') if p]
        if not path_parts:
            return False

        current = self.data

        for part in path_parts:
            if part not in current:
                current[part] = {}
            elif not isinstance(current[part], dict):
                return False
            current = current[part]

        return True

    def exists(self, path: str) -> bool:
        return self.get_node(path) is not None

    def normalize_path(self, current_path: str, target_path: str) -> str:
        if target_path.startswith('/'):
            return target_path

        if target_path == '..':
            parts = current_path.split('/')
            if len(parts) > 1:
                return '/'.join(parts[:-1]) or '/'
            return '/'

        if target_path == '.':
            return current_path

        if current_path == '/':
            return f'/{target_path}'
        else:
            return f'{current_path}/{target_path}'

    def remove_node(self, path: str) -> bool:
        """Удаляет узел (файл или каталог) по указанному пути"""
        path_parts = [p for p in path.split('/') if p]
        if not path_parts:
            return False

        *dirs, name = path_parts
        current = self.data

        # Находим родительский каталог
        for part in dirs:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return False

        # Удаляем узел
        if isinstance(current, dict) and name in current:
            del current[name]
            return True
        
        return False

    def move_directory(self, source_path: str, dest_path: str) -> bool:
        """Перемещает каталог со всем содержимым"""
        source_node = self.get_node(source_path)
        if not isinstance(source_node, dict):
            return False

        # Создаем целевой каталог
        if not self.create_directory(dest_path):
            return False

        # Рекурсивно копируем содержимое
        for item_name, item_data in source_node.items():
            item_source = f"{source_path}/{item_name}" if source_path != "/" else f"/{item_name}"
            item_dest = f"{dest_path}/{item_name}" if dest_path != "/" else f"/{item_name}"
            
            if isinstance(item_data, dict):
                # Это каталог
                if not self.move_directory(item_source, item_dest):
                    return False
            else:
                # Это файл
                content = self.read_file(item_source)
                if content is not None:
                    if not self.create_file(item_dest, content):
                        return False
                else:
                    return False

        return True

    def copy_node(self, source_path: str, dest_path: str) -> bool:
        """Копирует узел (файл или каталог)"""
        source_node = self.get_node(source_path)
        if source_node is None:
            return False

        if isinstance(source_node, str):
            # Это файл
            content = self.read_file(source_path)
            if content is not None:
                return self.create_file(dest_path, content)
        else:
            # Это каталог
            return self.move_directory(source_path, dest_path)
        
        return False