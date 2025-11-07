import os
import hashlib
from typing import Tuple


class LocalStorageService:
    def __init__(self, base_dir: str = "storage"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def _listing_dir(self, listing_id: int) -> str:
        path = os.path.join(self.base_dir, str(listing_id))
        os.makedirs(path, exist_ok=True)
        return path

    def save_file(self, listing_id: int, filename: str, file_bytes: bytes, version: int) -> Tuple[str, str]:
        dir_path = self._listing_dir(listing_id)
        name, ext = os.path.splitext(filename)
        versioned_name = f"{name}_v{version}{ext}"
        storage_path = os.path.join(dir_path, versioned_name)
        with open(storage_path, "wb") as f:
            f.write(file_bytes)
        sha256_hash = hashlib.sha256(file_bytes).hexdigest()
        return storage_path, sha256_hash


