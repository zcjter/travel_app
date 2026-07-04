from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel


# ── Auth ──────────────────────────────────────────────────────────
class UserRegister(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ── Media ─────────────────────────────────────────────────────────
class MediaResponse(BaseModel):
    id: int
    file_path: str
    file_type: str
    thumbnail_path: str
    exif: str
    file_size: int
    created_at: datetime

    class Config:
        from_attributes = True


# ── Moment ────────────────────────────────────────────────────────
class MomentCreate(BaseModel):
    trip_id: int
    content: str = ""
    location_name: str = ""
    media_ids: List[int] = []


class MomentUpdate(BaseModel):
    content: Optional[str] = None
    location_name: Optional[str] = None
    media_ids: Optional[List[int]] = None


class MomentResponse(BaseModel):
    id: int
    trip_id: int
    content: str
    location_name: str
    weather_info: str
    created_at: datetime
    updated_at: datetime
    media_list: List[MediaResponse] = []

    class Config:
        from_attributes = True


# ── Trip ──────────────────────────────────────────────────────────
class TripCreate(BaseModel):
    title: str
    cover_image: str = ""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: str = ""
    status: str = "planning"
    budget: Optional[float] = None
    destination: str = ""


class TripUpdate(BaseModel):
    title: Optional[str] = None
    cover_image: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None
    status: Optional[str] = None
    budget: Optional[float] = None
    destination: Optional[str] = None


class TripResponse(BaseModel):
    id: int
    title: str
    cover_image: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: str
    status: str
    budget: Optional[float] = None
    destination: str
    created_at: datetime
    moments: List[MomentResponse] = []

    class Config:
        from_attributes = True


# ── Stats ─────────────────────────────────────────────────────────
class YearlyDistribution(BaseModel):
    year: int
    count: int


class StatsSummary(BaseModel):
    total_trips: int = 0
    total_moments: int = 0
    total_photos: int = 0
    total_videos: int = 0
    total_cities: int = 0
    yearly_distribution: List[YearlyDistribution] = []


# ── Upload ────────────────────────────────────────────────────────
class ExifInfo(BaseModel):
    datetime: Optional[str] = None
    camera_model: Optional[str] = None
    aperture: Optional[str] = None
    shutter_speed: Optional[str] = None
    iso: Optional[str] = None
    focal_length: Optional[str] = None


class UploadResponse(BaseModel):
    id: int
    url: str
    thumbnail_url: str
    file_type: str
    file_size: int
    exif: ExifInfo
