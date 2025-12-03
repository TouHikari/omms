import sys
import json
import random
import asyncio
import pymysql
import re
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.settings import settings
from app.db.session import init_db, AsyncSessionLocal, engine
from app.models.record import MedicalRecord, RecordTemplate
from sqlalchemy import delete


def exec_sql_file(conn: pymysql.connections.Connection, sql_path: Path) -> None:
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


def reset_schema_with_sql() -> None:
    conn = pymysql.connect(
        host=settings.MYSQL_SERVER,
        user=settings.MYSQL_USER,
        password=settings.MYSQL_PASSWORD,
        database=settings.MYSQL_DB,
        port=settings.MYSQL_PORT,
        charset="utf8mb4",
        autocommit=False,
    )
    sql_path = ROOT.parent / "docs" / "omms.sql"
    exec_sql_file(conn, sql_path)
    conn.close()


async def seed_app_tables() -> None:
    await init_db()
    async with AsyncSessionLocal() as session:
        await session.execute(delete(MedicalRecord))
        await session.execute(delete(RecordTemplate))
        tpl1 = RecordTemplate(
            name="内科常用模板",
            scope="内科",
            fields_json=json.dumps([
                "chiefComplaint",
                "diagnosis",
                "prescriptions",
                "labs",
                "imaging",
            ], ensure_ascii=False),
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
            fields_json=json.dumps([
                "chiefComplaint",
                "diagnosis",
                "prescriptions",
            ], ensure_ascii=False),
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
        for i in range(20):
            rid = f"MR-{now.strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
            created_at = (now - timedelta(days=random.randint(0, 7))).strftime("%Y-%m-%d %H:%M")
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
                prescriptions_json=json.dumps(random.choice([["对乙酰氨基酚"], ["布洛芬"], []]), ensure_ascii=False),
                labs_json=json.dumps(random.choice([["血常规"], []]), ensure_ascii=False),
                imaging_json=json.dumps(random.choice([["胸片"], []]), ensure_ascii=False),
            )
            session.add(record)
        await session.commit()

    await engine.dispose()


def main() -> None:
    reset_schema_with_sql()
    asyncio.run(seed_app_tables())


if __name__ == "__main__":
    main()
