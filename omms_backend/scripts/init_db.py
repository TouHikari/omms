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


def migrate_schema_with_mysql(settings_obj) -> None:
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
    cur = conn.cursor()
    def table_exists(name: str) -> bool:
        cur.execute("SHOW TABLES LIKE %s", (name,))
        return cur.fetchone() is not None
    def column_exists(table: str, column: str) -> bool:
        cur.execute(f"SHOW COLUMNS FROM `{table}` LIKE %s", (column,))
        return cur.fetchone() is not None
    if table_exists("departments"):
        if not column_exists("departments", "parent_id"):
            cur.execute("ALTER TABLE departments ADD COLUMN parent_id BIGINT(20) NULL DEFAULT NULL AFTER description")
        if not column_exists("departments", "sort_order"):
            cur.execute("ALTER TABLE departments ADD COLUMN sort_order INT(11) NULL DEFAULT 0 AFTER parent_id")
    if table_exists("doctors"):
        if not column_exists("doctors", "doctor_name"):
            if column_exists("doctors", "name"):
                cur.execute("ALTER TABLE doctors CHANGE COLUMN name doctor_name VARCHAR(50) NOT NULL")
            else:
                cur.execute("ALTER TABLE doctors ADD COLUMN doctor_name VARCHAR(50) NOT NULL AFTER user_id")
        if not column_exists("doctors", "dept_id"):
            cur.execute("ALTER TABLE doctors ADD COLUMN dept_id BIGINT(20) NULL AFTER doctor_name")
            try:
                cur.execute("ALTER TABLE doctors ADD INDEX idx_doctors_dept_id (dept_id)")
            except Exception:
                pass
            try:
                cur.execute("ALTER TABLE doctors ADD CONSTRAINT doctors_ibfk_2 FOREIGN KEY (dept_id) REFERENCES departments(dept_id) ON DELETE RESTRICT ON UPDATE RESTRICT")
            except Exception:
                pass
            try:
                cur.execute("UPDATE doctors d LEFT JOIN departments dep ON dep.dept_name = d.department SET d.dept_id = dep.dept_id")
            except Exception:
                pass
        if column_exists("doctors", "intro") and not column_exists("doctors", "introduction"):
            cur.execute("ALTER TABLE doctors CHANGE COLUMN intro introduction TEXT NULL")
        if column_exists("doctors", "department"):
            try:
                cur.execute("ALTER TABLE doctors DROP COLUMN department")
            except Exception:
                pass
    if table_exists("doctor_schedules"):
        if not column_exists("doctor_schedules", "booked"):
            cur.execute("ALTER TABLE doctor_schedules ADD COLUMN booked INT(11) NULL DEFAULT 0 AFTER max_appointments")
    if table_exists("appointments"):
        if not column_exists("appointments", "schedule_id"):
            cur.execute("ALTER TABLE appointments ADD COLUMN schedule_id BIGINT(20) NULL AFTER doctor_id")
            try:
                cur.execute("ALTER TABLE appointments ADD INDEX idx_appointments_schedule_id (schedule_id)")
            except Exception:
                pass
            try:
                cur.execute("ALTER TABLE appointments ADD CONSTRAINT appointments_ibfk_3 FOREIGN KEY (schedule_id) REFERENCES doctor_schedules(schedule_id) ON DELETE CASCADE ON UPDATE RESTRICT")
            except Exception:
                pass
    conn.commit()
    cur.close()
    conn.close()


async def seed_app_tables(
    init_db_func, session_factory, engine_obj, seed_count: int = 20
) -> None:
    from sqlalchemy import delete, text
    from app.models.record import MedicalRecord, RecordTemplate
    from app.models.appointment import Department, Doctor, Schedule, Appointment
    from app.models.patient import Patient
    try:
        from app.core.security import get_password_hash as _pwd_hash
    except Exception:
        def _pwd_hash(p: str) -> str:
            return p

    await init_db_func()
    async with session_factory() as session:
        await session.execute(delete(MedicalRecord))
        await session.execute(delete(RecordTemplate))
        await session.execute(delete(Appointment))
        await session.execute(delete(Schedule))
        await session.execute(delete(Doctor))
        await session.execute(delete(Department))
        await session.execute(delete(Patient))
        await session.commit()

        now_dt = datetime.now()
        now_str = now_dt.strftime("%Y-%m-%d %H:%M:%S")

        dept_defs = [
            ("内科", "综合内科"),
            ("外科", "普通外科"),
            ("儿科", "儿童诊疗"),
            ("妇产科", "女性与产科"),
            ("眼科", "眼科诊疗"),
            ("耳鼻喉科", "耳鼻喉诊疗"),
            ("口腔科", "口腔与牙科"),
            ("皮肤科", "皮肤病诊疗"),
            ("骨科", "骨与关节"),
            ("心血管内科", "心血管诊疗"),
        ]

        dept_objs: list[Department] = []
        for idx, (n, d) in enumerate(dept_defs, start=1):
            dept = Department(
                dept_name=n,
                description=d,
                sort_order=idx,
                created_at=now_dt,
                updated_at=now_dt,
            )
            dept_objs.append(dept)
        session.add_all(dept_objs)
        await session.commit()

        dept_tpls = {
            "内科": {
                "fields": ["主诉", "现病史", "查体", "初步诊断", "处方", "检验", "影像"],
                "defaults": {
                    "chiefComplaint": "发热伴咳嗽3天，咽痛",
                    "diagnosis": "上呼吸道感染待查",
                    "prescriptions": ["对乙酰氨基酚片"],
                    "labs": ["血常规", "CRP"],
                    "imaging": ["胸片"],
                },
            },
            "外科": {
                "fields": ["主诉", "受伤机制", "查体", "影像", "诊断", "处置", "处方"],
                "defaults": {
                    "chiefComplaint": "右前臂外伤1天，局部疼痛肿胀",
                    "diagnosis": "右前臂软组织损伤",
                    "prescriptions": ["布洛芬缓释胶囊"],
                    "labs": ["凝血功能"],
                    "imaging": ["右臂X光"],
                },
            },
            "儿科": {
                "fields": ["主诉", "喂养史", "疫苗史", "体温", "诊断", "处方"],
                "defaults": {
                    "chiefComplaint": "咳嗽2天，无发热",
                    "diagnosis": "小儿上呼吸道感染",
                    "prescriptions": ["止咳糖浆"],
                    "labs": ["血常规"],
                    "imaging": [],
                },
            },
            "妇产科": {
                "fields": ["主诉", "末次月经", "妊娠周数", "胎动", "诊断", "处方", "检查"],
                "defaults": {
                    "chiefComplaint": "孕检复诊",
                    "diagnosis": "妊娠期随访",
                    "prescriptions": ["叶酸片"],
                    "labs": ["孕检套餐"],
                    "imaging": ["产科超声"],
                },
            },
            "眼科": {
                "fields": ["主诉", "视力", "裂隙灯检查", "诊断", "处方", "检查"],
                "defaults": {
                    "chiefComplaint": "视物模糊1周",
                    "diagnosis": "干眼症待查",
                    "prescriptions": ["人工泪液"],
                    "labs": [],
                    "imaging": ["眼底照相"],
                },
            },
            "耳鼻喉科": {
                "fields": ["主诉", "耳鼻喉查体", "诊断", "处方", "检查"],
                "defaults": {
                    "chiefComplaint": "鼻塞流涕3天",
                    "diagnosis": "急性鼻炎",
                    "prescriptions": ["氯雷他定片"],
                    "labs": [],
                    "imaging": ["鼻窦CT"],
                },
            },
            "口腔科": {
                "fields": ["主诉", "口腔检查", "诊断", "处方", "检查"],
                "defaults": {
                    "chiefComplaint": "牙龈肿痛2天",
                    "diagnosis": "龋齿伴牙龈炎",
                    "prescriptions": ["甲硝唑片"],
                    "labs": [],
                    "imaging": ["牙片"],
                },
            },
            "皮肤科": {
                "fields": ["主诉", "皮损描述", "过敏史", "诊断", "处方", "检验"],
                "defaults": {
                    "chiefComplaint": "面部皮疹瘙痒1周",
                    "diagnosis": "过敏性皮炎",
                    "prescriptions": ["炉甘石洗剂"],
                    "labs": ["过敏原筛查"],
                    "imaging": [],
                },
            },
            "骨科": {
                "fields": ["主诉", "受伤时间", "查体", "影像", "诊断", "处置"],
                "defaults": {
                    "chiefComplaint": "膝关节疼痛3天，活动受限",
                    "diagnosis": "膝关节扭伤",
                    "prescriptions": ["双氯芬酸钠缓释片"],
                    "labs": ["炎症指标"],
                    "imaging": ["关节X光"],
                },
            },
            "心血管内科": {
                "fields": ["主诉", "心率血压", "心电图", "诊断", "处方", "检验"],
                "defaults": {
                    "chiefComplaint": "胸闷心悸1周",
                    "diagnosis": "心律不齐待查",
                    "prescriptions": ["倍他乐克片"],
                    "labs": ["心肌酶谱"],
                    "imaging": ["心电图"],
                },
            },
        }

        tpl_objs: list[RecordTemplate] = []
        for dept in dept_objs:
            cfg = dept_tpls.get(dept.dept_name) or {
                "fields": ["主诉", "诊断", "处方"],
                "defaults": {
                    "chiefComplaint": "主诉待填写",
                    "diagnosis": "待诊断",
                    "prescriptions": [],
                    "labs": [],
                    "imaging": [],
                },
            }
            tpl = RecordTemplate(
                name=f"{dept.dept_name}通用模板",
                scope=dept.dept_name,
                fields_json=json.dumps(cfg["fields"], ensure_ascii=False),
                defaults_json=json.dumps(cfg["defaults"], ensure_ascii=False),
            )
            tpl_objs.append(tpl)
        session.add_all(tpl_objs)
        await session.commit()

        # seed identity groups and admin
        async def upsert_user(username: str, password: str, email: str | None, real_name: str, role_id: int, phone: str | None = None) -> int:
            res = await session.execute(text("SELECT user_id FROM users WHERE username=:u OR email=:u"), {"u": username})
            row = res.first()
            if not row:
                await session.execute(
                    text(
                        """
                        INSERT INTO users (username,password,email,phone,real_name,status,created_at,updated_at,role_id)
                        VALUES (:username,:password,:email,:phone,:real_name,1,:created,:updated,:role_id)
                        """
                    ),
                    {
                        "username": username,
                        "password": _pwd_hash(password),
                        "email": email,
                        "phone": phone,
                        "real_name": real_name,
                        "created": now_str,
                        "updated": now_str,
                        "role_id": role_id,
                    },
                )
            else:
                await session.execute(
                    text(
                        """
                        UPDATE users
                        SET password=:password, email=:email, phone=:phone, real_name=:real_name,
                            status=1, updated_at=:updated, role_id=:role_id
                        WHERE user_id=:user_id
                        """
                    ),
                    {
                        "password": _pwd_hash(password),
                        "email": email,
                        "phone": phone,
                        "real_name": real_name,
                        "updated": now_str,
                        "role_id": role_id,
                        "user_id": int(row[0]),
                    },
                )
            res2 = await session.execute(text("SELECT user_id FROM users WHERE username=:username"), {"username": username})
            return int(res2.first()[0])

        admin_uid = await upsert_user("admin@omms", "admin123", "admin@omms", "系统管理员", 1)
        # doctor
        surnames = ["赵","钱","孙","李","周","吴","郑","王","冯","陈","褚","卫","蒋","沈","韩","杨","朱","秦","尤","许","何","吕","施","张","孔","曹","严","华","金","魏","陶","姜","戚","谢","邹","喻","柏","水","窦","章","云","苏","潘","葛","奚","范","彭","郎","鲁","韦"]
        given = ["伟","芳","娜","敏","静","强","磊","军","洋","勇","艳","杰","娟","涛","明","超","刚","玲","佳","丹","龙","博","涵","哲","晨","瑞","坤","宁","婷","露","婧","斌","浩","凯","倩","萌","璐","文","雪","璟","昕","昊","奕","璇","梓","可"]
        used_names: set[str] = set()

        doc_users: list[int] = []
        doctor_objs: list[Doctor] = []
        for di, dept in enumerate(dept_objs, start=1):
            cnt = random.randint(2, 3)
            for k in range(1, cnt + 1):
                uname = f"doc_{di:02d}_{k:02d}"
                rname = None
                while True:
                    rname = random.choice(surnames) + random.choice(given)
                    if rname not in used_names:
                        used_names.add(rname)
                        break
                uid = await upsert_user(uname, "omms123", f"{uname}@omms", rname, 2)
                title = random.choice(["主任医师","副主任医师","主治医师","医师"])
                spec_map = {
                    "内科": "呼吸内科",
                    "外科": "普外科",
                    "儿科": "儿科综合",
                    "妇产科": "产科门诊",
                    "眼科": "眼底与视光",
                    "耳鼻喉科": "耳鼻喉综合",
                    "口腔科": "牙体牙髓",
                    "皮肤科": "皮肤过敏",
                    "骨科": "关节外科",
                    "心血管内科": "心内科综合",
                }
                doc = Doctor(
                    user_id=uid,
                    doctor_name=rname,
                    dept_id=dept.dept_id,
                    title=title,
                    specialty=spec_map.get(dept.dept_name, None),
                    available_status=1,
                    created_at=now_dt,
                    updated_at=now_dt,
                )
                doctor_objs.append(doc)
        session.add_all(doctor_objs)
        await session.commit()

        nurse_uid = await upsert_user("nurse001", "omms123", "nurse001@omms", "王护士", 4)
        res_nurse = await session.execute(text("SELECT nurse_id FROM nurses WHERE user_id=:uid"), {"uid": nurse_uid})
        if not res_nurse.first():
            await session.execute(
                text(
                    """
                    INSERT INTO nurses (user_id,name,department,title,created_at,updated_at)
                    VALUES (:uid,:name,:dept,:title,:created,:updated)
                    """
                ),
                {
                    "uid": nurse_uid,
                    "name": "王护士",
                    "dept": "内科",
                    "title": "护士",
                    "created": now_str,
                    "updated": now_str,
                },
            )

        # patient
        base_patients = max(seed_count * 2, 40)
        patient_objs: list[Patient] = []
        for i in range(1, base_patients + 1):
            uname = f"patient_{i:03d}"
            rname = None
            while True:
                rname = random.choice(surnames) + random.choice(given)
                if rname not in used_names:
                    used_names.add(rname)
                    break
            uid = await upsert_user(uname, "omms123", f"{uname}@omms", rname, 3)
            gender = random.choice([0, 1])
            year = random.randint(1965, 2015)
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            birthday = f"{year:04d}-{month:02d}-{day:02d}"
            id_card = f"110101{year:04d}{month:02d}{day:02d}{random.randint(1000,9999)}"
            pat = Patient(
                user_id=uid,
                name=rname,
                gender=gender,
                birthday=birthday,
                id_card=id_card,
                created_at=now_dt,
                updated_at=now_dt,
            )
            patient_objs.append(pat)
        session.add_all(patient_objs)
        await session.commit()

        schedule_objs: list[Schedule] = []
        appt_objs: list[Appointment] = []
        for doc in doctor_objs:
            days = [1, 3, 5, 7, 9, 11]
            for d in days:
                work_date = (now_dt + timedelta(days=d)).date()
                s = Schedule(
                    doctor_id=doc.doctor_id,
                    work_date=work_date,
                    start_time=datetime.strptime("08:00:00", "%H:%M:%S").time(),
                    end_time=datetime.strptime("17:30:00", "%H:%M:%S").time(),
                    max_appointments=16,
                    booked=0,
                    status=1,
                    created_at=now_dt,
                    updated_at=now_dt,
                )
                schedule_objs.append(s)
        session.add_all(schedule_objs)
        await session.commit()

        for s in schedule_objs:
            base_slots = 8
            start_dt = datetime.combine(s.work_date, s.start_time)
            patients_pick = random.sample(patient_objs, k=min(base_slots, len(patient_objs)))
            used_count = 0
            for i, p in enumerate(patients_pick):
                appt_time = start_dt + timedelta(minutes=20 * i)
                status = random.choice([0, 1, 2])
                symptom = random.choice(["发热咳嗽","腹痛","头痛","乏力","皮疹","牙痛","视物模糊","鼻塞流涕"]) 
                ap = Appointment(
                    patient_id=p.patient_id,
                    doctor_id=s.doctor_id,
                    schedule_id=s.schedule_id,
                    appt_time=appt_time,
                    status=status,
                    symptom_desc=symptom,
                    created_at=now_dt,
                    updated_at=now_dt,
                )
                appt_objs.append(ap)
                if status != 2:
                    used_count += 1
            s.booked = used_count
        session.add_all(appt_objs)
        await session.commit()

        record_count = max(seed_count * 10, 200)
        rec_objs: list[MedicalRecord] = []
        tpl_by_scope = {t.scope: t for t in tpl_objs}
        for _ in range(record_count):
            ap = random.choice(appt_objs)
            dept_id = None
            for d in doctor_objs:
                if d.doctor_id == ap.doctor_id:
                    dept_id = d.dept_id
                    break
            pat = None
            for p in patient_objs:
                if p.patient_id == ap.patient_id:
                    pat = p
                    break
            created_at = (now_dt - timedelta(days=random.randint(0, 30), hours=random.randint(0, 12))).strftime("%Y-%m-%d %H:%M")
            rid = f"MR-{created_at[:10].replace('-', '')}-{random.randint(100000,999999)}"
            scope_name = None
            for dept in dept_objs:
                if dept.dept_id == dept_id:
                    scope_name = dept.dept_name
                    break
            tpl = tpl_by_scope.get(scope_name)
            chief = random.choice(["发热伴咳嗽","腹痛","头痛","皮疹","胸闷心悸","关节疼痛","牙龈肿痛"]) 
            diag = random.choice(["上呼吸道感染","胃炎","偏头痛","皮炎","心律不齐","关节炎","龋齿"]) 
            pres = random.choice([["对乙酰氨基酚"],["布洛芬"],["阿莫西林"],["氯雷他定"],["维生素C"],[]])
            labs = random.choice([["血常规"],["肝肾功能"],[]])
            imgs = random.choice([["胸片"],["牙片"],[]])
            rec = MedicalRecord(
                id=rid,
                dept_id=dept_id or 1,
                doctor_id=ap.doctor_id,
                patient_id=ap.patient_id,
                patient_name=pat.name if pat else None,
                created_at=created_at,
                status=random.choice(["draft","finalized","cancelled"]),
                template_id=tpl.id if tpl else None,
                chief_complaint=chief,
                diagnosis=diag,
                prescriptions_json=json.dumps(pres, ensure_ascii=False),
                labs_json=json.dumps(labs, ensure_ascii=False),
                imaging_json=json.dumps(imgs, ensure_ascii=False),
            )
            rec_objs.append(rec)
        session.add_all(rec_objs)
        await session.commit()

    await engine_obj.dispose()


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="init_db", description="Initialize database schema and seed demo data"
    )
    parser.add_argument("--mode", choices=["app", "full", "migrate"], default="app")
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
            f"sqlite+aiosqlite:///{(ROOT / 'test.db').resolve().as_posix()}"
        )

    from app.core.settings import settings as settings_obj
    from app.db.session import (
        init_db as init_db_func,
        AsyncSessionLocal as session_factory,
        engine as engine_obj,
    )

    if args.mode == "full" and not args.skip_sql:
        reset_schema_with_sql(settings_obj, Path(args.sql))
    else:
        migrate_schema_with_mysql(settings_obj)
    asyncio.run(
        seed_app_tables(init_db_func, session_factory, engine_obj, args.seed_count)
    )


if __name__ == "__main__":
    main()
