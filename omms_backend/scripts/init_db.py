import sys
import json
import random
import asyncio
import re
import argparse
import os
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def exec_sql_file(conn, sql_path: Path) -> None:
    cur = conn.cursor()
    cur.execute("SET NAMES utf8mb4")
    cur.execute("SET FOREIGN_KEY_CHECKS=0")
    content = sql_path.read_text(encoding="utf-8")
    content = re.sub(r"/\*[\s\S]*?\*/", "", content)
    statements = []
    buf = []
    for line in content.splitlines():
        s = line.strip()
        if not s or s.startswith("--"):
            continue
        buf.append(line)
        if s.endswith(";"):
            statements.append("\n".join(buf))
            buf = []
    for stmt in statements:
        cur.execute(stmt)
    conn.commit()
    cur.close()


def reset_schema_with_sql(settings_obj, sql_path: Path) -> None:
    import pymysql

    conn = pymysql.connect(
        host=settings_obj.MYSQL_SERVER,
        user=settings_obj.MYSQL_USER,
        password=settings_obj.MYSQL_PASSWORD,
        database=settings_obj.MYSQL_DB,
        port=settings_obj.MYSQL_PORT,
        charset="utf8mb4",
        autocommit=False,
    )
    if sql_path.exists():
        exec_sql_file(conn, sql_path)
    conn.close()


async def seed_app_tables(
    init_db_func, session_factory, engine_obj, seed_count: int = 20
) -> None:
    from sqlalchemy import delete
    from app.models.record import MedicalRecord, RecordTemplate

    await init_db_func()
    async with session_factory() as session:
        await session.execute(delete(MedicalRecord))
        await session.execute(delete(RecordTemplate))
        tpl1 = RecordTemplate(
            name="内科常用模板",
            scope="内科",
            fields_json=json.dumps(
                [
                    "chiefComplaint",
                    "diagnosis",
                    "prescriptions",
                    "labs",
                    "imaging",
                ],
                ensure_ascii=False,
            ),
            defaults_json=json.dumps(
                {
                    "chiefComplaint": "主诉：",
                    "diagnosis": "初步诊断：",
                    "prescriptions": ["对乙酰氨基酚"],
                    "labs": ["血常规"],
                    "imaging": [],
                },
                ensure_ascii=False,
            ),
        )
        tpl2 = RecordTemplate(
            name="儿科常用模板",
            scope="儿科",
            fields_json=json.dumps(
                [
                    "chiefComplaint",
                    "diagnosis",
                    "prescriptions",
                ],
                ensure_ascii=False,
            ),
            defaults_json=json.dumps(
                {
                    "chiefComplaint": "发热咳嗽",
                    "diagnosis": "上呼吸道感染",
                    "prescriptions": ["布洛芬"],
                },
                ensure_ascii=False,
            ),
        )
        session.add_all([tpl1, tpl2])
        await session.commit()
        now = datetime.now()
        for i in range(seed_count):
            rid = f"MR-{now.strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
            created_at = (now - timedelta(days=random.randint(0, 7))).strftime(
                "%Y-%m-%d %H:%M"
            )
            record = MedicalRecord(
                id=rid,
                dept_id=random.choice([1, 2, 3]),
                doctor_id=random.choice([1, 2, 3]),
                patient_id=random.choice([10001, 10002, 10003]),
                patient_name=random.choice(["张三", "李四", "王五"]),
                created_at=created_at,
                status=random.choice(["draft", "finalized", "cancelled"]),
                template_id=random.choice([1, 2]),
                chief_complaint=random.choice(["发热2天伴咳嗽", "腹痛1周", "头痛半月"]),
                diagnosis=random.choice(["上呼吸道感染？", "胃炎？", "偏头痛？"]),
                prescriptions_json=json.dumps(
                    random.choice([["对乙酰氨基酚"], ["布洛芬"], []]),
                    ensure_ascii=False,
                ),
                labs_json=json.dumps(
                    random.choice([["血常规"], []]), ensure_ascii=False
                ),
                imaging_json=json.dumps(
                    random.choice([["胸片"], []]), ensure_ascii=False
                ),
            )
            session.add(record)
        await session.commit()

    await engine_obj.dispose()


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="init_db", description="Initialize database schema and seed demo data"
    )
    parser.add_argument("--mode", choices=["app", "full"], default="app")
    parser.add_argument(
        "--sql", default=str((ROOT.parent / "docs" / "omms.sql").resolve())
    )
    parser.add_argument("--skip-sql", action="store_true")
    parser.add_argument("--sqlite", action="store_true")
    parser.add_argument("--dsn", default=None)
    parser.add_argument("--seed-count", type=int, default=20)
    args = parser.parse_args()

    if args.dsn:
        os.environ["DATABASE_URL"] = args.dsn
    elif args.sqlite:
        os.environ["DATABASE_URL"] = (
            f"sqlite+aiosqlite:///{(ROOT / 'omms_dev.db').resolve().as_posix()}"
        )

    from app.settings import settings as settings_obj
    from app.db.session import (
        init_db as init_db_func,
        AsyncSessionLocal as session_factory,
        engine as engine_obj,
    )

    if args.mode == "full" and not args.skip_sql:
        reset_schema_with_sql(settings_obj, Path(args.sql))
    asyncio.run(
        seed_app_tables(init_db_func, session_factory, engine_obj, args.seed_count)
    )


if __name__ == "__main__":
    main()
