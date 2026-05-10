from pydantic import BaseModel
from typing import Literal

class DeviceStatus(BaseModel):
    online: bool
    device_name: str|None = None
    device_id: str|None = None
    mount_path: str | None = None
    status: Literal["offline", "mounted", "watching", "error"]
    message: str|None = None


class DirectoryChangeEvent(BaseModel):
    has_new_data: bool
    change_type: Literal["created", "modified", "deleted", "stable", "ignored"]
    file_name: str | None = None
    file_path: str | None = None
    directory_path: str | None = None

