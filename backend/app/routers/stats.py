from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import Trip, Moment, Media

router = APIRouter(prefix="/stats", tags=["统计"])


@router.get("/summary", response_model=dict)
async def get_stats_summary(db: AsyncSession = Depends(get_db)):
    """获取仪表盘统计数据"""
    # 旅程总数
    result = await db.execute(select(func.count(Trip.id)))
    total_trips = result.scalar() or 0

    # 记录总数
    result = await db.execute(select(func.count(Moment.id)))
    total_moments = result.scalar() or 0

    # 照片 + 视频总数
    result = await db.execute(
        select(func.count(Media.id)).where(Media.file_type == "image")
    )
    total_photos = result.scalar() or 0

    result = await db.execute(
        select(func.count(Media.id)).where(Media.file_type == "video")
    )
    total_videos = result.scalar() or 0

    # 去过的城市数
    result = await db.execute(
        select(func.count(func.distinct(Trip.destination)))
        .where(Trip.destination != "", Trip.destination.isnot(None))
    )
    total_cities = result.scalar() or 0

    # 年度旅程分布
    result = await db.execute(
        select(
            func.strftime("%Y", Trip.start_date).label("year"),
            func.count(Trip.id).label("count"),
        )
        .where(Trip.start_date.isnot(None))
        .group_by("year")
        .order_by("year")
    )
    rows = result.all()
    yearly_distribution = [{"year": int(r.year), "count": r.count} for r in rows if r.year]

    return {
        "data": {
            "total_trips": total_trips,
            "total_moments": total_moments,
            "total_photos": total_photos,
            "total_videos": total_videos,
            "total_cities": total_cities,
            "yearly_distribution": yearly_distribution,
        }
    }
