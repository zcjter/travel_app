"""
数据库迁移：将 media.moment_id 从 NOT NULL 改为 NULLABLE
（上传图片时尚未关联 moment）
运行: python migrate_fix_media_nullable.py
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
            # 检查当前 schema
            inspector = inspect(sync_conn)
            media_cols = {col["name"]: col for col in inspector.get_columns("media")}
            if media_cols.get("moment_id", {}).get("nullable", False):
                print("  media.moment_id 已经是 NULLABLE，跳过")
                return

            print("  重建 media 表（moment_id → NULLABLE）...")

            sync_conn.execute(text("PRAGMA foreign_keys = OFF"))

            sync_conn.execute(text("""
                CREATE TABLE media_new (
                    id INTEGER NOT NULL PRIMARY KEY,
                    moment_id INTEGER REFERENCES moments(id) ON DELETE CASCADE,
                    file_path VARCHAR(256) NOT NULL,
                    file_type VARCHAR(16) DEFAULT 'image',
                    thumbnail_path VARCHAR(256) DEFAULT '',
                    exif TEXT DEFAULT '',
                    file_size INTEGER DEFAULT 0,
                    created_at DATETIME
                )
            """))
            sync_conn.execute(text("""
                INSERT INTO media_new (id, moment_id, file_path, file_type, thumbnail_path, exif, file_size, created_at)
                SELECT id, moment_id, file_path, file_type, thumbnail_path, exif, file_size, created_at FROM media
            """))
            sync_conn.execute(text("DROP TABLE media"))
            sync_conn.execute(text("ALTER TABLE media_new RENAME TO media"))

            sync_conn.execute(text("PRAGMA foreign_keys = ON"))

            print("  [OK] media.moment_id 改为 NULLABLE")

        await conn.run_sync(do_migrate)

    print("Migration done!")


if __name__ == "__main__":
    asyncio.run(migrate())
