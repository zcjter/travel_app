"""
数据库迁移：删除 moments 表中的 lat / lon 列（兼容旧版 SQLite）
运行: python migrate_remove_latlon.py
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

import asyncio
from sqlalchemy import inspect, text
from app.database import engine


async def migrate():
    async with engine.begin() as conn:
        def do_migrate(sync_conn):
            inspector = inspect(sync_conn)
            columns = [col["name"] for col in inspector.get_columns("moments")]
            to_drop = [c for c in ("lat", "lon") if c in columns]

            if not to_drop:
                print("  ⏭️  lat/lon 列不存在，跳过迁移")
                return

            print(f"  需删除列: {', '.join(to_drop)}")

            # 关闭外键检查，重建表（兼容旧版 SQLite 不支持 DROP COLUMN）
            sync_conn.execute(text("PRAGMA foreign_keys = OFF"))

            sync_conn.execute(text("""
                CREATE TABLE moments_new (
                    id INTEGER NOT NULL PRIMARY KEY,
                    trip_id INTEGER NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
                    content TEXT DEFAULT '',
                    location_name VARCHAR(128) DEFAULT '',
                    weather_info TEXT DEFAULT '',
                    created_at DATETIME,
                    updated_at DATETIME
                )
            """))
            sync_conn.execute(text("""
                INSERT INTO moments_new (id, trip_id, content, location_name, weather_info, created_at, updated_at)
                SELECT id, trip_id, content, location_name, weather_info, created_at, updated_at FROM moments
            """))
            sync_conn.execute(text("DROP TABLE moments"))
            sync_conn.execute(text("ALTER TABLE moments_new RENAME TO moments"))

            sync_conn.execute(text("PRAGMA foreign_keys = ON"))

            for col in to_drop:
                print(f"  [OK] {col} removed")

        await conn.run_sync(do_migrate)

    print("Migration done!")


if __name__ == "__main__":
    asyncio.run(migrate())
