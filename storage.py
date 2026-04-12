import json
import os
from datetime import datetime
from typing import List, Dict, Any

class Storage:
    def __init__(self):
        self.data_dir = self._get_safe_data_dir()
        self._ensure_directory()
        self.items_file = os.path.join(self.data_dir, "items.json")
        self.items = self._load_items()

    def _get_safe_data_dir(self) -> str:
        try:
            home = os.path.expanduser("~")
            if not home or not os.path.exists(home):
                return os.getcwd()
            
            data_dir = os.path.join(home, "file_transfer_data")
            return data_dir
        except Exception:
            return os.getcwd()

    def _ensure_directory(self):
        try:
            if not os.path.exists(self.data_dir):
                os.makedirs(self.data_dir, exist_ok=True)
        except Exception as e:
            print(f"Warning: Could not create data directory: {e}")
            self.data_dir = os.getcwd()

    def _load_items(self) -> List[Dict[str, Any]]:
        try:
            if os.path.exists(self.items_file):
                with open(self.items_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return data
                    return []
            return []
        except json.JSONDecodeError as e:
            print(f"Error: Corrupted JSON file: {e}")
            return []
        except Exception as e:
            print(f"Error loading items: {e}")
            return []

    def _save_items(self):
        try:
            with open(self.items_file, "w", encoding="utf-8") as f:
                json.dump(self.items, f, ensure_ascii=False, indent=2)
        except PermissionError:
            print("Error: No permission to save file")
        except Exception as e:
            print(f"Error saving items: {e}")

    def add_item(self, item_type: str, content: str, title: str = "") -> Dict[str, Any]:
        try:
            item = {
                "id": f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                "type": item_type,
                "title": title.strip() if title else self._get_default_title(item_type),
                "content": content,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.items.insert(0, item)
            self._save_items()
            return item
        except Exception as e:
            print(f"Error adding item: {e}")
            return None

    def _get_default_title(self, item_type: str) -> str:
        titles = {
            "text": "Text",
            "link": "Link", 
            "file": "File",
            "image": "Image"
        }
        base_title = titles.get(item_type, "Item")
        count = sum(1 for i in self.items if i.get("type") == item_type) + 1
        return f"{base_title} {count}"

    def delete_item(self, item_id: str) -> bool:
        try:
            original_count = len(self.items)
            self.items = [i for i in self.items if i.get("id") != item_id]
            if len(self.items) < original_count:
                self._save_items()
                return True
            return False
        except Exception as e:
            print(f"Error deleting item: {e}")
            return False

    def get_items(self, filter_type: str = None) -> List[Dict[str, Any]]:
        try:
            if filter_type:
                return [i for i in self.items if i.get("type") == filter_type]
            return list(self.items)
        except Exception:
            return []

    def get_item_by_id(self, item_id: str) -> Dict[str, Any]:
        try:
            for item in self.items:
                if item.get("id") == item_id:
                    return dict(item)
            return None
        except Exception:
            return None

    def search_items(self, keyword: str) -> List[Dict[str, Any]]:
        try:
            if not keyword:
                return []
            keyword_lower = keyword.lower()
            return [
                i for i in self.items
                if keyword_lower in (i.get("title") or "").lower()
                or keyword_lower in (i.get("content") or "").lower()
            ]
        except Exception:
            return []

    def get_storage_info(self) -> Dict[str, Any]:
        total_size = 0
        try:
            if os.path.exists(self.data_dir):
                for filename in os.listdir(self.data_dir):
                    filepath = os.path.join(self.data_dir, filename)
                    if os.path.isfile(filepath):
                        try:
                            total_size += os.path.getsize(filepath)
                        except:
                            pass
        except:
            pass
        
        type_counts = {"text": 0, "link": 0, "file": 0, "image": 0}
        for item in self.items:
            item_type = item.get("type")
            if item_type in type_counts:
                type_counts[item_type] += 1
        
        return {
            "total_items": len(self.items),
            "storage_size": total_size,
            "by_type": type_counts
        }

    def get_file_path(self, filename: str) -> str:
        return os.path.join(self.data_dir, filename)

    def get_data_dir(self) -> str:
        return self.data_dir
