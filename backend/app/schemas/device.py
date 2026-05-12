from pydantic import BaseModel
from typing import Literal, Optional

class DeviceStatus(BaseModel):
    online: bool
    device_name: Optional[str] = None
    device_id: Optional[str] = None
    mount_path: Optional[str] = None
    status: Literal["offline", "mounted", "watching", "error"]
    message: Optional[str] = None


class DirectoryChangeEvent(BaseModel):
    has_new_data: bool
    change_type: Literal["created", "modified", "deleted", "stable", "ignored"]
    file_name: Optional[str] = None
    file_path: Optional[str] = None
    directory_path: Optional[str] = None

