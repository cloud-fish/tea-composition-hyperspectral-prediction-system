import os
from typing import Literal

from app.config import settings


DeviceStatusValue = Literal["offline", "mounted", "watching", "error"]
ChangeTypeValue = Literal["created", "modified", "deleted", "stable", "ignored"]


class DeviceService:
    """设备挂载目录状态探测服务。"""

    def __init__(self) -> None:
        self.device_name = settings.DEVICE_NAME
        self.device_id = settings.DEVICE_ID
        self.mount_path = settings.DEVICE_MOUNT_PATH
        self.online = False
        self.status: DeviceStatusValue = "offline"
        self.message = "设备未接入"
        self.has_new_data = False
        self.change_type: ChangeTypeValue = "ignored"
        self.file_name: str | None = None
        self.file_path: str | None = None
        self.directory_path = self.mount_path
        self._snapshot: dict[str, tuple[float, int]] = {}
        self._initialized = False

    def refresh_status(self) -> None:
        """刷新设备挂载目录状态。"""
        self.directory_path = self.mount_path

        if not self.mount_path:
            self.online = False
            self.status = "error"
            self.message = "未配置设备挂载目录"
            return

        if not os.path.exists(self.mount_path):
            self.online = False
            self.status = "offline"
            self.message = f"未检测到挂载目录: {self.mount_path}"
            return

        if not os.path.isdir(self.mount_path):
            self.online = False
            self.status = "error"
            self.message = f"挂载路径不是目录: {self.mount_path}"
            return

        if not os.access(self.mount_path, os.R_OK):
            self.online = False
            self.status = "error"
            self.message = f"挂载目录不可读: {self.mount_path}"
            return

        self.online = True
        self.status = "mounted"
        self.message = f"设备已接入，挂载目录可访问: {self.mount_path}"

    def refresh_directory_change(self) -> None:
        """扫描挂载目录并返回最近一次文件变化。"""
        self.refresh_status()
        self.directory_path = self.mount_path

        if not self.online:
            self.has_new_data = False
            self.change_type = "ignored"
            self.file_name = None
            self.file_path = None
            return

        current_snapshot = self._build_snapshot()

        if not self._initialized:
            self._snapshot = current_snapshot
            self._initialized = True
            self.has_new_data = False
            self.change_type = "stable"
            self.file_name = None
            self.file_path = None
            return

        created_files = sorted(
            set(current_snapshot) - set(self._snapshot),
            key=lambda path: current_snapshot[path][0],
            reverse=True,
        )
        modified_files = sorted(
            [
                path
                for path, stat in current_snapshot.items()
                if path in self._snapshot and stat != self._snapshot[path]
            ],
            key=lambda path: current_snapshot[path][0],
            reverse=True,
        )
        deleted_files = sorted(set(self._snapshot) - set(current_snapshot))

        if created_files:
            latest_path = created_files[0]
            self.has_new_data = True
            self.change_type = "created"
            self.file_path = latest_path
            self.file_name = os.path.basename(latest_path)
        elif modified_files:
            latest_path = modified_files[0]
            self.has_new_data = True
            self.change_type = "modified"
            self.file_path = latest_path
            self.file_name = os.path.basename(latest_path)
        elif deleted_files:
            latest_path = deleted_files[0]
            self.has_new_data = False
            self.change_type = "deleted"
            self.file_path = latest_path
            self.file_name = os.path.basename(latest_path)
        else:
            self.has_new_data = False
            self.change_type = "stable"
            self.file_path = None
            self.file_name = None

        self._snapshot = current_snapshot

    def _build_snapshot(self) -> dict[str, tuple[float, int]]:
        """构建当前目录文件快照，用于后续变化比对。"""
        snapshot: dict[str, tuple[float, int]] = {}

        for root, _, files in os.walk(self.mount_path):
            for file_name in files:
                if file_name.startswith("."):
                    continue

                file_path = os.path.join(root, file_name)

                try:
                    stat = os.stat(file_path)
                except OSError:
                    continue

                snapshot[file_path] = (stat.st_mtime, stat.st_size)

        return snapshot


device_service = DeviceService()
