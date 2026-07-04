import os
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Trip, Moment, Media
from app.schemas import TripCreate, TripUpdate


def to_url(file_path: str) -> str:
    """将绝对路径转为 /uploads/ 开头的 URL"""
    if not file_path:
        return ""
    # 取 uploads/ 之后的部分
    idx = file_path.find("uploads")
    if idx >= 0:
        return "/" + file_path[idx:].replace("\\", "/")
    return file_path

router = APIRouter(prefix="/trips", tags=["旅程"])


@router.get("", response_model=dict)
async def list_trips(
    year: Optional[int] = Query(None, description="按年份筛选"),
    include_moments: bool = Query(False, description="是否同时返回记录"),
    db: AsyncSession = Depends(get_db),
):
    """获取所有旅程列表，支持按年份筛选"""
    query = select(Trip).order_by(Trip.created_at.desc())

    if year is not None:
        query = query.where(
            Trip.start_date >= date(year, 1, 1),
            Trip.start_date <= date(year, 12, 31),
        )

    if include_moments:
        query = query.options(selectinload(Trip.moments).selectinload(Moment.media_list))

    result = await db.execute(query)
    trips = result.scalars().all()

    def build_moment_data(m):
        return {
            "id": m.id,
            "content": m.content,
            "location_name": m.location_name,
            "created_at": m.created_at.isoformat() + "Z",
            "media_list": [
                {
                    "id": media.id,
                    "file_path": to_url(media.file_path),
                    "file_type": media.file_type,
                    "thumbnail_path": to_url(media.thumbnail_path),
                }
                for media in m.media_list
            ],
        }

    return {
        "data": [
            {
                "id": t.id,
                "title": t.title,
                "cover_image": t.cover_image,
                "start_date": t.start_date.isoformat() if t.start_date else None,
                "end_date": t.end_date.isoformat() if t.end_date else None,
                "description": t.description,
                "status": t.status,
                "budget": t.budget,
                "destination": t.destination,
                "created_at": t.created_at.isoformat() + "Z",
                "moments": [build_moment_data(m) for m in t.moments] if include_moments else [],
            }
            for t in trips
        ],
        "total": len(trips),
    }


@router.post("", response_model=dict, status_code=201)
async def create_trip(data: TripCreate, db: AsyncSession = Depends(get_db)):
    """创建新旅程"""
    trip = Trip(**data.model_dump())
    db.add(trip)
    await db.commit()
    await db.refresh(trip)
    return {"data": {"id": trip.id, "title": trip.title, "message": "旅程创建成功"}}


@router.get("/{trip_id}", response_model=dict)
async def get_trip(trip_id: int, db: AsyncSession = Depends(get_db)):
    """获取旅程详情（含所有 Moments）"""
    query = (
        select(Trip)
        .where(Trip.id == trip_id)
        .options(selectinload(Trip.moments).selectinload(Moment.media_list))
    )
    result = await db.execute(query)
    trip = result.scalar_one_or_none()

    if not trip:
        raise HTTPException(status_code=404, detail="旅程不存在")

    moments_data = []
    for m in trip.moments:
        moments_data.append({
            "id": m.id,
            "trip_id": m.trip_id,
            "content": m.content,
            "location_name": m.location_name,
            "weather_info": m.weather_info,
            "created_at": m.created_at.isoformat() + "Z",
            "updated_at": m.updated_at.isoformat() + "Z",
            "media_list": [
                {
                    "id": media.id,
                    "file_path": to_url(media.file_path),
                    "file_type": media.file_type,
                    "thumbnail_path": to_url(media.thumbnail_path),
                    "exif": media.exif,
                    "file_size": media.file_size,
                    "created_at": media.created_at.isoformat() + "Z",
                }
                for media in m.media_list
            ],
        })

    return {
        "data": {
            "id": trip.id,
            "title": trip.title,
            "cover_image": trip.cover_image,
            "start_date": trip.start_date.isoformat() if trip.start_date else None,
            "end_date": trip.end_date.isoformat() if trip.end_date else None,
            "description": trip.description,
            "status": trip.status,
            "budget": trip.budget,
            "destination": trip.destination,
            "created_at": trip.created_at.isoformat() + "Z",
            "moments": moments_data,
        }
    }


@router.put("/{trip_id}", response_model=dict)
async def update_trip(trip_id: int, data: TripUpdate, db: AsyncSession = Depends(get_db)):
    """更新旅程信息"""
    result = await db.execute(select(Trip).where(Trip.id == trip_id))
    trip = result.scalar_one_or_none()

    if not trip:
        raise HTTPException(status_code=404, detail="旅程不存在")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(trip, key, value)

    await db.commit()
    return {"message": "旅程更新成功"}


@router.delete("/{trip_id}", response_model=dict)
async def delete_trip(
    trip_id: int,
    delete_files: bool = Query(False, description="是否同时物理删除媒体文件"),
    db: AsyncSession = Depends(get_db),
):
    """删除旅程，可选级联删除媒体文件"""
    result = await db.execute(
        select(Trip)
        .where(Trip.id == trip_id)
        .options(selectinload(Trip.moments).selectinload(Moment.media_list))
    )
    trip = result.scalar_one_or_none()

    if not trip:
        raise HTTPException(status_code=404, detail="旅程不存在")

    if delete_files:
        import os
        for moment in trip.moments:
            for media in moment.media_list:
                for path in [media.file_path, media.thumbnail_path]:
                    if path and os.path.exists(path):
                        try:
                            os.remove(path)
                        except OSError:
                            pass

    await db.delete(trip)
    await db.commit()
    return {"message": "旅程已删除"}


@router.get("/{trip_id}/moments", response_model=dict)
async def list_trip_moments(trip_id: int, db: AsyncSession = Depends(get_db)):
    """获取旅程下的所有记录"""
    query = (
        select(Moment)
        .where(Moment.trip_id == trip_id)
        .options(selectinload(Moment.media_list))
        .order_by(Moment.created_at.asc())
    )
    result = await db.execute(query)
    moments = result.scalars().all()

    return {
        "data": [
            {
                "id": m.id,
                "trip_id": m.trip_id,
                "content": m.content,
                "location_name": m.location_name,
                "weather_info": m.weather_info,
            "created_at": m.created_at.isoformat() + "Z",
                "updated_at": m.updated_at.isoformat() + "Z",
            "media_list": [
                {
                    "id": media.id,
                    "file_path": to_url(media.file_path),
                    "file_type": media.file_type,
                    "thumbnail_path": to_url(media.thumbnail_path),
                    "file_size": media.file_size,
                }
                for media in m.media_list
            ],
        }
        for m in moments
    ],
        "total": len(moments),
    }
