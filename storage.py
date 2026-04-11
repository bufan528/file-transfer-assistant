import json
import os
from datetime import datetime
from typing import List, Dict, Any

class Storage:
    def __init__(self):
        self.data_dir = os.path.join(os.path.expanduser("~"), "文件传输助手数据")
        os.makedirs(self.data_dir, exist_ok=True)
        self.items_file = os.path.join(self.data_dir, "items.json")
        self.items = self._load_items()

    def _load_items(self) -> List[Dict[str, Any]]:
        if os.path.exists(self.items_file):
            try:
                with open(self.items_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []

    def _save_items(self):
        with open(self.items_file, "w", encoding="utf-8") as f:
            json.dump(self.items, f, ensure_ascii=False, indent=2)

    def add_item(self, item_type: str, content: str, title: str = "") -> Dict[str, Any]:
        item = {
            "id": str(datetime.now().timestamp()),
            "type": item_type,
            "title": title or self._get_default_title(item_type),
            "content": content,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.items.insert(0, item)
        self._save_items()
        return item

    def _get_default_title(self, item_type: str) -> str:
        titles = {
            "text": "文本",
            "link": "链接",
            "file": "文件",
            "image": "图片"
        }
        count = sum(1 for i in self.items if i["type"] == item_type) + 1
        return f"{titles.get(item_type, '内容')}_{count}"

    def delete_item(self, item_id: str) -> bool:
        self.items = [i for i in self.items if i["id"] != item_id]
        self._save_items()
        return True

    def get_items(self, filter_type: str = None) -> List[Dict[str, Any]]:
        if filter_type:
            return [i for i in self.items if i["type"] == filter_type]
        return self.items

    def get_item_by_id(self, item_id: str) -> Dict[str, Any]:
        for item in self.items:
            if item["id"] == item_id:
                return item
        return None

    def search_items(self, keyword: str) -> List[Dict[str, Any]]:
        keyword = keyword.lower()
        return [
            i for i in self.items
            if keyword in i.get("title", "").lower()
            or keyword in i.get("content", "").lower()
        ]

    def get_storage_info(self) -> Dict[str, Any]:
        total_size = sum(
            os.path.getsize(os.path.join(self.data_dir, f))
            for f in os.listdir(self.data_dir)
            if os.path.isfile(os.path.join(self.data_dir, f))
        )
        return {
            "total_items": len(self.items),
            "storage_size": total_size,
            "by_type": {
                t: len([i for i in self.items if i["type"] == t])
                for t in ["text", "link", "file", "image"]
            }
        }

    def get_file_path(self, filename: str) -> str:
        return os.path.join(self.data_dir, filename)