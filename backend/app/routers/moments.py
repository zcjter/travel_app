import json
import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Moment, Media
from app.schemas import MomentCreate, MomentUpdate


def to_url(file_path: str) -> str:
    """将绝对路径转为 /uploads/ 开头的 URL"""
    if not file_path:
        return ""
    idx = file_path.find("uploads")
    if idx >= 0:
        return "/" + file_path[idx:].replace("\\", "/")
    return file_path

router = APIRouter(prefix="/moments", tags=["记录"])


@router.post("", response_model=dict, status_code=201)
async def create_moment(data: MomentCreate, db: AsyncSession = Depends(get_db)):
    """创建一条记录（关联图片与文字）"""
    moment = Moment(
        trip_id=data.trip_id,
        content=data.content,
        location_name=data.location_name,
    )
    db.add(moment)
    await db.flush()  # 获取 moment.id

    # 关联已上传的媒体文件
    if data.media_ids:
        result = await db.execute(
            select(Media).where(Media.id.in_(data.media_ids))
        )
        media_list = result.scalars().all()
        for media in media_list:
            media.moment_id = moment.id

    await db.commit()
    await db.refresh(moment)

    return {
        "data": {
            "id": moment.id,
            "trip_id": moment.trip_id,
            "content": moment.content,
            "location_name": moment.location_name,
            "created_at": moment.created_at.isoformat() + "Z",
        },
        "message": "记录创建成功",
    }


@router.get("/{moment_id}", response_model=dict)
async def get_moment(moment_id: int, db: AsyncSession = Depends(get_db)):
    """获取单条记录详情"""
    query = (
        select(Moment)
        .where(Moment.id == moment_id)
        .options(selectinload(Moment.media_list))
    )
    result = await db.execute(query)
    moment = result.scalar_one_or_none()

    if not moment:
        raise HTTPException(status_code=404, detail="记录不存在")

    return {
        "data": {
            "id": moment.id,
            "trip_id": moment.trip_id,
            "content": moment.content,
            "location_name": moment.location_name,
            "weather_info": moment.weather_info,
            "created_at": moment.created_at.isoformat() + "Z",
            "updated_at": moment.updated_at.isoformat() + "Z",
            "media_list": [
                {
                    "id": media.id,
                    "file_path": to_url(media.file_path),
                    "file_type": media.file_type,
                    "thumbnail_path": to_url(media.thumbnail_path),
                    "exif": media.exif,
                    "file_size": media.file_size,
                }
                for media in moment.media_list
            ],
        }
    }


@router.put("/{moment_id}", response_model=dict)
async def update_moment(
    moment_id: int, data: MomentUpdate, db: AsyncSession = Depends(get_db)
):
    """更新记录（支持修改文字、关联媒体）"""
    result = await db.execute(
        select(Moment).where(Moment.id == moment_id).options(selectinload(Moment.media_list))
    )
    moment = result.scalar_one_or_none()

    if not moment:
        raise HTTPException(status_code=404, detail="记录不存在")

    update_data = data.model_dump(exclude_unset=True)

    # 处理 media_ids
    media_ids = update_data.pop("media_ids", None)
    if media_ids is not None:
        # 解除旧关联
        for media in moment.media_list:
            media.moment_id = None
        await db.flush()
        # 建立新关联
        if media_ids:
            result = await db.execute(
                select(Media).where(Media.id.in_(media_ids))
            )
            for media in result.scalars().all():
                media.moment_id = moment.id

    # 更新其他字段
    for key, value in update_data.items():
        setattr(moment, key, value)

    await db.commit()
    return {"message": "记录更新成功"}


@router.delete("/{moment_id}", response_model=dict)
async def delete_moment(moment_id: int, db: AsyncSession = Depends(get_db)):
    """删除单条记录"""
    result = await db.execute(
        select(Moment)
        .where(Moment.id == moment_id)
        .options(selectinload(Moment.media_list))
    )
    moment = result.scalar_one_or_none()

    if not moment:
        raise HTTPException(status_code=404, detail="记录不存在")

    # 物理删除关联文件
    import os
    for media in moment.media_list:
        for path in [media.file_path, media.thumbnail_path]:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass

    await db.delete(moment)
    await db.commit()
    return {"message": "记录已删除"}
