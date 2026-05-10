from fastapi import APIRouter, HTTPException

from app.schemas.device import DeviceStatus, DirectoryChangeEvent
from app.services.device_service import device_service

router = APIRouter()

@router.get("/device/status", response_model=DeviceStatus)
async def get_device_status():
    """获取设备状态"""
    try:
        device_service.refresh_status()

        return DeviceStatus(
            online=device_service.online,
            device_name=device_service.device_name,
            device_id=device_service.device_id,
            mount_path=device_service.mount_path,
            status=device_service.status,
            message=device_service.message
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取设备状态失败过程中发生错误: {str(e)}")

@router.get("/device/directory/change", response_model=DirectoryChangeEvent)
async def get_directory_change():
    """获取目录变更事件"""
    try:
        device_service.refresh_directory_change()
        return DirectoryChangeEvent(
            has_new_data=device_service.has_new_data,
            change_type=device_service.change_type,
            file_name=device_service.file_name,
            file_path=device_service.file_path,
            directory_path=device_service.directory_path
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取目录变更事件失败过程中发生错误: {str(e)}")
