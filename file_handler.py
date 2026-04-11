import os
import shutil
import base64
from datetime import datetime
from storage import Storage
from PIL import Image
import io

class FileHandler:
    def __init__(self, storage: Storage):
        self.storage = storage
        self.files_dir = os.path.join(storage.data_dir, "files")
        self.images_dir = os.path.join(storage.data_dir, "images")
        os.makedirs(self.files_dir, exist_ok=True)
        os.makedirs(self.images_dir, exist_ok=True)

    def save_file(self, source_path: str, custom_name: str = None) -> dict:
        if not os.path.exists(source_path):
            return {"success": False, "error": "文件不存在"}

        filename = custom_name or os.path.basename(source_path)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        safe_filename = f"{timestamp}_{filename}"
        dest_path = os.path.join(self.files_dir, safe_filename)

        try:
            shutil.copy2(source_path, dest_path)
            file_size = os.path.getsize(dest_path)
            return {
                "success": True,
                "filename": safe_filename,
                "original_name": filename,
                "path": dest_path,
                "size": file_size
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def save_text_as_file(self, text: str, filename: str) -> dict:
        try:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            safe_filename = f"{timestamp}_{filename}.txt"
            file_path = os.path.join(self.files_dir, safe_filename)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(text)

            return {
                "success": True,
                "filename": safe_filename,
                "path": file_path,
                "size": os.path.getsize(file_path)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def save_link(self, url: str, title: str = "") -> dict:
        if not url.startswith(("http://", "https://")):
            return {"success": False, "error": "无效的链接格式"}

        if not title:
            title = url.split("/")[-1] if url.split("/")[-1] else "链接"

        return {
            "success": True,
            "url": url,
            "title": title
        }

    def save_image_from_data(self, image_data: bytes, original_name: str = "image") -> dict:
        try:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            ext = self._get_image_ext(image_data)
            safe_filename = f"{timestamp}_{original_name}.{ext}"
            file_path = os.path.join(self.images_dir, safe_filename)

            with open(file_path, "wb") as f:
                f.write(image_data)

            return {
                "success": True,
                "filename": safe_filename,
                "path": file_path,
                "size": os.path.getsize(file_path)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_image_ext(self, image_data: bytes) -> str:
        if image_data[:8] == b"\x89PNG\r\n\x1a\n":
            return "png"
        elif image_data[:2] == b"\xff\xd8":
            return "jpg"
        elif image_data[:4] == b"GIF8":
            return "gif"
        elif image_data[:4] == b"RIFF" and image_data[8:12] == b"WEBP":
            return "webp"
        return "jpg"

    def delete_file(self, filename: str, file_type: str = "file") -> bool:
        if file_type == "image":
            file_path = os.path.join(self.images_dir, filename)
        else:
            file_path = os.path.join(self.files_dir, filename)

        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                return True
            except:
                return False
        return False

    def get_file_info(self, filename: str, file_type: str = "file") -> dict:
        if file_type == "image":
            file_path = os.path.join(self.images_dir, filename)
        else:
            file_path = os.path.join(self.files_dir, filename)

        if os.path.exists(file_path):
            return {
                "exists": True,
                "size": os.path.getsize(file_path),
                "path": file_path
            }
        return {"exists": False}

    def format_size(self, size_bytes: int) -> str:
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f}TB"