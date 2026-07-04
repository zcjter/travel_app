import os
import uuid
import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from PIL import Image
from io import BytesIO

from app.database import get_db
from app.models import Media
from app.schemas import UploadResponse, ExifInfo

router = APIRouter(prefix="/upload", tags=["上传"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
THUMBNAIL_DIR = os.path.join(UPLOAD_DIR, "thumbnails")
MAX_THUMBNAIL_SIZE = (300, 300)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".mp4", ".mov", ".avi"}


def parse_exif(file_path: str) -> dict:
    """解析图片 EXIF 信息"""
    result = {
        "datetime": None,
        "camera_model": None,
        "aperture": None,
        "shutter_speed": None,
        "iso": None,
        "focal_length": None,
    }

    try:
        import exifread
        with open(file_path, "rb") as f:
            tags = exifread.process_file(f, details=False)

        # 拍摄时间
        if "EXIF DateTimeOriginal" in tags:
            result["datetime"] = str(tags["EXIF DateTimeOriginal"])
        elif "Image DateTime" in tags:
            result["datetime"] = str(tags["Image DateTime"])

        # 设备型号
        if "Image Model" in tags:
            result["camera_model"] = str(tags["Image Model"])
        elif "Image Make" in tags:
            result["camera_model"] = str(tags["Image Make"])

        # 光圈
        if "EXIF FNumber" in tags:
            result["aperture"] = str(tags["EXIF FNumber"])

        # 快门
        if "EXIF ExposureTime" in tags:
            result["shutter_speed"] = str(tags["EXIF ExposureTime"])

        # ISO
        if "EXIS ISOSpeedRatings" in tags or "EXIF ISOSpeedRatings" in tags:
            key = "EXIF ISOSpeedRatings" if "EXIF ISOSpeedRatings" in tags else "EXIS ISOSpeedRatings"
            result["iso"] = str(tags[key])

        # 焦距
        if "EXIF FocalLength" in tags:
            result["focal_length"] = str(tags["EXIF FocalLength"])

    except Exception:
        pass  # 没有 EXIF 也能正常返回

    return result


async def save_thumbnail(file_path: str, thumbnail_path: str):
    """生成缩略图"""
    try:
        img = Image.open(file_path)
        img.thumbnail(MAX_THUMBNAIL_SIZE, Image.LANCZOS)
        # 如果是 RGBA，转为 RGB
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.save(thumbnail_path, "JPEG", quality=80)
    except Exception:
        pass  # 缩略图生成失败不影响主流程


@router.post("", response_model=dict)
async def upload_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """上传媒体文件，返回 EXIF 与预览信息"""
    # 校验文件扩展名
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式: {ext}，支持: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # 判断文件类型
    file_type = "video" if ext in {".mp4", ".mov", ".avi"} else "image"

    # 生成唯一文件名
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    # 保存文件
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    file_size = len(content)

    # 解析 EXIF（仅图片）
    exif_data = {}
    thumbnail_path = ""
    if file_type == "image":
        exif_data = parse_exif(file_path)

        # 生成缩略图
        thumb_name = f"{uuid.uuid4().hex}.jpg"
        thumbnail_path = os.path.join(THUMBNAIL_DIR, thumb_name)
        await save_thumbnail(file_path, thumbnail_path)

    # 写入数据库
    media = Media(
        file_path=file_path,
        file_type=file_type,
        thumbnail_path=thumbnail_path,
        exif=json.dumps(exif_data, ensure_ascii=False),
        file_size=file_size,
    )
    db.add(media)
    await db.commit()
    await db.refresh(media)

    return {
        "data": {
            "id": media.id,
            "url": f"/uploads/{unique_name}",
            "thumbnail_url": f"/uploads/thumbnails/{os.path.basename(thumbnail_path)}" if thumbnail_path else "",
            "file_type": file_type,
            "file_size": file_size,
            "exif": {
                "datetime": exif_data.get("datetime"),
                "camera_model": exif_data.get("camera_model"),
                "aperture": exif_data.get("aperture"),
                "shutter_speed": exif_data.get("shutter_speed"),
                "iso": exif_data.get("iso"),
                "focal_length": exif_data.get("focal_length"),
            },
        }
    }


@router.post("/cover", response_model=dict)
async def upload_cover(file: UploadFile = File(...)):
    """上传旅程封面图，返回 URL（不创建 Media 记录）"""
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"不支持的文件格式: {ext}")
    unique_name = f"cover_{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    # 生成缩略图
    thumb_name = f"cover_{uuid.uuid4().hex}.jpg"
    thumbnail_path = os.path.join(THUMBNAIL_DIR, thumb_name)
    try:
        img = Image.open(file_path)
        img.thumbnail((600, 400), Image.LANCZOS)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.save(thumbnail_path, "JPEG", quality=85)
    except Exception:
        thumbnail_path = ""
    return {
        "data": {
            "url": f"/uploads/{unique_name}",
            "thumbnail_url": f"/uploads/thumbnails/{os.path.basename(thumbnail_path)}" if thumbnail_path else "",
        }
    }
