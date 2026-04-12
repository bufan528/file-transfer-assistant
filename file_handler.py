import os
import shutil
from datetime import datetime
from storage import Storage

class FileHandler:
    def __init__(self, storage: Storage):
        self.storage = storage
        self.files_dir = os.path.join(storage.get_data_dir(), "files")
        self.images_dir = os.path.join(storage.get_data_dir(), "images")
        
        try:
            os.makedirs(self.files_dir, exist_ok=True)
            os.makedirs(self.images_dir, exist_ok=True)
        except Exception as e:
            print(f"Warning: Could not create file directories: {e}")

    def save_file(self, source_path: str, custom_name: str = None) -> dict:
        if not source_path or not os.path.exists(source_path):
            return {"success": False, "error": "File not found"}

        try:
            filename = custom_name or os.path.basename(source_path)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            safe_filename = f"{timestamp}_{filename}"
            dest_path = os.path.join(self.files_dir, safe_filename)

            shutil.copy2(source_path, dest_path)
            
            if os.path.exists(dest_path):
                file_size = os.path.getsize(dest_path)
                return {
                    "success": True,
                    "filename": safe_filename,
                    "original_name": filename,
                    "path": dest_path,
                    "size": file_size
                }
            return {"success": False, "error": "Failed to copy file"}
            
        except PermissionError:
            return {"success": False, "error": "Permission denied"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def save_text_as_file(self, text: str, filename: str) -> dict:
        if not text:
            return {"success": False, "error": "No content to save"}

        try:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            safe_name = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_')).strip()
            if not safe_name:
                safe_name = "text"
            safe_filename = f"{timestamp}_{safe_name}.txt"
            file_path = os.path.join(self.files_dir, safe_filename)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(text)

            if os.path.exists(file_path):
                return {
                    "success": True,
                    "filename": safe_filename,
                    "path": file_path,
                    "size": os.path.getsize(file_path)
                }
            return {"success": False, "error": "Failed to create file"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def save_link(self, url: str, title: str = "") -> dict:
        if not url:
            return {"success": False, "error": "URL is empty"}

        url = url.strip()
        if not url.startswith(("http://", "https://", "ftp://")):
            return {"success": False, "error": "Invalid URL format. Must start with http:// or https://"}

        if not title or not title.strip():
            title = url.split("/")[-1] if "/" in url else "Link"
            title = title.split("?")[0]
            if len(title) > 50:
                title = title[:50]

        return {
            "success": True,
            "url": url,
            "title": title.strip() if isinstance(title, str) else "Link"
        }

    def save_image_from_data(self, image_data: bytes, original_name: str = "image") -> dict:
        if not image_data:
            return {"success": False, "error": "No image data"}

        try:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            ext = self._get_image_ext(image_data)
            safe_name = "".join(c for c in original_name if c.isalnum() or c in (' ', '-', '_')).strip()
            if not safe_name:
                safe_name = "image"
            safe_filename = f"{timestamp}_{safe_name}.{ext}"
            file_path = os.path.join(self.images_dir, safe_filename)

            with open(file_path, "wb") as f:
                f.write(image_data)

            if os.path.exists(file_path):
                return {
                    "success": True,
                    "filename": safe_filename,
                    "path": file_path,
                    "size": os.path.getsize(file_path)
                }
            return {"success": False, "error": "Failed to save image"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_image_ext(self, image_data: bytes) -> str:
        if not image_data or len(image_data) < 4:
            return "jpg"
        
        try:
            if image_data[:8] == b"\x89PNG\r\n\x1a\n":
                return "png"
            elif image_data[:2] == b"\xff\xd8":
                return "jpg"
            elif image_data[:6] == b"GIF87a" or image_data[:6] == b"GIF89a":
                return "gif"
            elif len(image_data) > 12 and image_data[:4] == b"RIFF" and image_data[8:12] == b"WEBP":
                return "webp"
            else:
                return "jpg"
        except:
            return "jpg"

    def delete_file(self, filename: str, file_type: str = "file") -> bool:
        if not filename:
            return False
            
        try:
            if file_type == "image":
                file_path = os.path.join(self.images_dir, filename)
            else:
                file_path = os.path.join(self.files_dir, filename)

            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except PermissionError:
            print("Permission denied when deleting file")
            return False
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False

    def get_file_info(self, filename: str, file_type: str = "file") -> dict:
        if not filename:
            return {"exists": False}
            
        try:
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
        except Exception:
            return {"exists": False}

    @staticmethod
    def format_size(size_bytes: int) -> str:
        if size_bytes <= 0:
            return "0 B"
        
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        
        return f"{size_bytes:.1f} TB"
