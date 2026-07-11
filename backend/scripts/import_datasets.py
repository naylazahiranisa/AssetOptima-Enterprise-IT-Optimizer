#!/usr/bin/env python3
"""Import all CSV datasets into the database, mapping custom IDs to UUIDs."""

import asyncio
import csv
import logging
import uuid
from datetime import datetime
from pathlib import Path

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import AsyncSessionLocal
from app.database.base import Base
from app.database.connection import engine
from app.models.company import Company
from app.models.department import Department
from app.models.employee import Employee
from app.models.asset_category import AssetCategory
from app.models.software_category import SoftwareCategory
from app.models.software import Software
from app.models.license_model import License
from app.models.asset import Asset
from app.models.software_usage_log import SoftwareUsageLog
from app.models.audit_log import AuditLog
from app.models.notification import Notification
from app.models.vendor import Vendor
from app.models.location import Location

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-8s  %(message)s")
logger = logging.getLogger(__name__)

RAW = Path(r"D:\SB4_University\ArtificialIntelligence\UAS_Nayla\AssetOptima\datasets\raw")

# ---------------------------------------------------------------------------
# ID mapping: CSV custom IDs → UUIDs
# ---------------------------------------------------------------------------
_id_map: dict[str, str] = {}

def _id(csv_id: str) -> str:
    if csv_id not in _id_map:
        _id_map[csv_id] = str(uuid.uuid4())
    return _id_map[csv_id]

def _ts(val: str) -> datetime | None:
    if not val or val.strip() == "":
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S%z", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(val.strip(), fmt)
        except ValueError:
            continue
    return None

def _date(val: str) -> datetime | None:
    if not val or val.strip() == "":
        return None
    try:
        return datetime.strptime(val.strip(), "%Y-%m-%d")
    except ValueError:
        return None

def _bool(val: str) -> bool:
    return val.strip().upper() == "TRUE"

def _int(val: str) -> int | None:
    if not val or val.strip() == "":
        return None
    try:
        return int(float(val.strip()))
    except ValueError:
        return None

def _float(val: str) -> float | None:
    if not val or val.strip() == "":
        return None
    try:
        return float(val.strip())
    except ValueError:
        return None

# ---------------------------------------------------------------------------
# CSV readers
# ---------------------------------------------------------------------------
def _read_csv(filename: str) -> list[dict]:
    path = RAW / filename
    if not path.exists():
        logger.warning("SKIP: %s not found", path)
        return []
    with open(path, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

# ---------------------------------------------------------------------------
# Seeding functions
# ---------------------------------------------------------------------------

async def seed_companies(db: AsyncSession) -> dict[str, str]:
    """Return {csv_id: uuid} mapping for companies."""
    rows = _read_csv("companies.csv")
    mapping = {}
    for row in rows:
        uid = _id(row["company_id"])
        mapping[row["company_id"]] = uid
        db.add(Company(
            id=uid,
            name=row["name"],
            code=row["code"],
            address=row.get("address"),
            phone=row.get("phone"),
            email=row.get("email"),
            is_active=True,
        ))
    await db.commit()
    logger.info("  → %d companies", len(rows))
    return mapping

async def seed_departments(db: AsyncSession, company_map: dict[str, str]) -> dict[str, str]:
    rows = _read_csv("departments.csv")
    mapping = {}
    for row in rows:
        uid = _id(row["department_id"])
        mapping[row["department_id"]] = uid
        db.add(Department(
            id=uid,
            name=row["name"],
            code=row["code"],
            company_id=company_map.get(row["company_id"]),
            is_active=_bool(row.get("is_active", "TRUE")),
        ))
    await db.commit()
    logger.info("  → %d departments", len(rows))
    return mapping

async def seed_asset_categories(db: AsyncSession) -> dict[str, str]:
    rows = _read_csv("asset_categories.csv")
    mapping = {}
    for row in rows:
        uid = _id(row["category_id"])
        mapping[row["category_id"]] = uid
        db.add(AssetCategory(
            id=uid,
            name=row["name"],
            code=row["code"],
        ))
    await db.commit()
    logger.info("  → %d asset categories", len(rows))
    return mapping

async def seed_employees(db: AsyncSession, company_map: dict[str, str], dept_map: dict[str, str]) -> dict[str, str]:
    rows = _read_csv("employees.csv")
    mapping = {}
    for row in rows:
        uid = _id(row["employee_id"])
        mapping[row["employee_id"]] = uid
        db.add(Employee(
            id=uid,
            employee_id=row["employee_id"],
            full_name=row["full_name"],
            email=row["email"],
            phone=row.get("phone"),
            position=row.get("position"),
            department_id=dept_map.get(row.get("department_id", "")),
            company_id=company_map.get(row.get("company_id", "")),
            is_active=row.get("employment_status", "active").strip().lower() == "active",
        ))
    await db.commit()
    logger.info("  → %d employees", len(rows))
    return mapping

async def seed_vendors(db: AsyncSession) -> dict[str, str]:
    vendors = [
        ("Microsoft Corporation", "MSFT"),
        ("Adobe Inc.", "ADBE"),
        ("Slack Technologies", "SLACK"),
        ("Zoom Video Communications", "ZOOM"),
        ("Atlassian Corporation", "ATLA"),
        ("Salesforce Inc.", "SFDC"),
        ("Google LLC", "GOOG"),
        ("Amazon Web Services", "AWS"),
        ("Oracle Corporation", "ORCL"),
        ("SAP SE", "SAP"),
        ("Apple Inc.", "AAPL"),
        ("Dell Technologies", "DELL"),
        ("Cisco Systems", "CSCO"),
        ("VMware Inc.", "VMW"),
        ("IBM Corporation", "IBM"),
    ]
    mapping = {}
    for name, code in vendors:
        uid = str(uuid.uuid4())
        mapping[code] = uid
        db.add(Vendor(id=uid, name=name, code=code, is_active=True))
    await db.commit()
    logger.info("  → %d vendors", len(vendors))
    return mapping

async def seed_locations(db: AsyncSession, company_map: dict[str, str]) -> dict[str, str]:
    locations_data = [
        ("Jakarta HQ", "JKT-HQ", "Jl. Gatot Subroto No. 500", "Jakarta"),
        ("Bandung Office", "BDG-OFF", "Jl. Riau No. 120", "Bandung"),
        ("Surabaya Office", "SBY-OFF", "Jl. Tunjungan No. 50", "Surabaya"),
        ("Yogyakarta Office", "YOG-OFF", "Jl. Kaliurang No. 80", "Yogyakarta"),
        ("Medan Office", "MDN-OFF", "Jl. Sisingamangaraja No. 200", "Medan"),
    ]
    comp_id = next(iter(company_map.values())) if company_map else None
    mapping = {}
    for name, code, addr, city in locations_data:
        uid = str(uuid.uuid4())
        mapping[code] = uid
        db.add(Location(id=uid, name=name, code=code, company_id=comp_id, address=addr, city=city))
    await db.commit()
    logger.info("  → %d locations", len(locations_data))
    return mapping

async def seed_software_categories(db: AsyncSession) -> dict[str, str]:
    cats = [
        ("Analytics & BI", "ANL"),
        ("Creative & Design", "CRE"),
        ("Communication", "COM"),
        ("Development", "DEV"),
        ("Productivity", "PROD"),
        ("Security", "SEC"),
        ("Cloud Services", "CLD"),
        ("Database", "DB"),
    ]
    mapping = {}
    for name, code in cats:
        uid = str(uuid.uuid4())
        mapping[code] = uid
        db.add(SoftwareCategory(id=uid, name=name, code=code, is_active=True))
    await db.commit()
    logger.info("  → %d software categories", len(cats))
    return mapping

async def seed_software(db: AsyncSession, vendor_map: dict[str, str], sw_cat_map: dict[str, str]) -> dict[str, str]:
    rows = _read_csv("software_catalog.csv")
    mapping = {}
    vendor_lookup = {v.lower(): k for k, v in [
        ("Microsoft", "MSFT"), ("Adobe", "ADBE"), ("Slack", "SLACK"),
        ("Zoom", "ZOOM"), ("Atlassian", "ATLA"), ("Salesforce", "SFDC"),
        ("Google", "GOOG"), ("Amazon", "AWS"), ("Oracle", "ORCL"),
        ("SAP", "SAP"),
    ]}
    for row in rows:
        uid = _id(row["software_id"])
        mapping[row["software_id"]] = uid
        vendor_code = vendor_lookup.get(row.get("vendor", "").lower())
        sw_cat_code = {"Analytics": "ANL", "Creative": "CRE", "Communication": "COM",
                       "Development": "DEV", "Productivity": "PROD", "Security": "SEC"}.get(row.get("category", ""))
        db.add(Software(
            id=uid,
            name=row["name"],
            vendor_id=vendor_map.get(vendor_code) if vendor_code else None,
            category_id=sw_cat_map.get(sw_cat_code) if sw_cat_code else None,
            license_type="subscription" if _bool(row.get("is_cloud", "TRUE")) else "perpetual",
            monthly_cost=_float(row.get("monthly_cost_per_seat")),
            annual_cost=_float(row.get("annual_cost_per_seat")),
            status="active",
        ))
    await db.commit()
    logger.info("  → %d software", len(rows))
    return mapping

async def seed_licenses(db: AsyncSession, sw_map: dict[str, str]) -> dict[str, str]:
    rows = _read_csv("licenses.csv")
    mapping = {}
    for row in rows:
        uid = _id(row["license_id"])
        mapping[row["license_id"]] = uid
        db.add(License(
            id=uid,
            license_key=row.get("license_id", uid),
            software_id=sw_map.get(row["software_id"]),
            renewal_date=_date(row.get("renewal_date", "")),
            status=row.get("status", "active"),
            max_seats=_int(row.get("total_licenses", "1")) or 1,
            allocated_seats=_int(row.get("used_licenses", "0")) or 0,
            monthly_cost=_float(row.get("monthly_cost")),
            annual_cost=_float(row.get("annual_cost")),
        ))
    await db.commit()
    logger.info("  → %d licenses", len(rows))
    return mapping

async def seed_assets(db: AsyncSession, cat_map: dict[str, str], emp_map: dict[str, str]) -> dict[str, str]:
    rows = _read_csv("assets.csv")
    mapping = {}
    for row in rows:
        uid = _id(row["asset_id"])
        mapping[row["asset_id"]] = uid
        qr_value = f"{row.get('asset_tag', uid)}-{row.get('serial_number', uid)}"

        status = row.get("status", "available").strip().lower()
        condition = row.get("condition", "good").strip().lower()

        db.add(Asset(
            id=uid,
            asset_code=row.get("asset_tag", uid),
            serial_number=row.get("serial_number"),
            name=f"{row.get('brand', '')} {row.get('model', '')}".strip() or "Asset",
            category_id=cat_map.get(row["category_id"]),
            status=status if status in ("available","assigned","maintenance","lost","retired") else "available",
            condition=condition if condition in ("excellent","good","fair","damaged","broken") else "good",
            purchase_date=_date(row.get("purchase_date", "")),
            purchase_price=_float(row.get("purchase_price")),
            current_employee_id=emp_map.get(row.get("current_employee_id", "")),
            qr_value=qr_value,
            notes=row.get("notes"),
        ))
    await db.commit()
    logger.info("  → %d assets", len(rows))
    return mapping

async def seed_usage_logs(db: AsyncSession, emp_map: dict[str, str], sw_map: dict[str, str], dept_map: dict[str, str]):
    rows = _read_csv("software_usage_logs.csv")
    count = 0
    BATCH = 500
    dept_by_emp: dict[str, str] = {}
    for row in rows:
        emp_id = emp_map.get(row.get("employee_id", ""))
        if not emp_id:
            continue
        sw_id = sw_map.get(row.get("software_id", ""))
        if not sw_id:
            continue
        emp_csv_id = row["employee_id"]
        if emp_csv_id not in dept_by_emp:
            dept_by_emp[emp_csv_id] = dept_map.get(row.get("department", "").replace(" ", ""), row.get("department", ""))
        if count % BATCH == 0 and count > 0:
            await db.commit()
        login_time = None
        if row.get("login_date") and row.get("login_time"):
            try:
                login_time = datetime.strptime(f"{row['login_date']} {row['login_time']}", "%Y-%m-%d %H:%M:%S")
            except ValueError:
                login_time = None
        db.add(SoftwareUsageLog(
            id=str(uuid.uuid4()),
            employee_id=emp_id,
            software_id=sw_id,
            login_time=login_time or datetime.now(),
            session_duration_seconds=_int(row.get("session_duration_minutes", "")) and _int(row["session_duration_minutes"]) * 60,
            device_name=row.get("device"),
            ip_address=row.get("ip_address"),
            os=row.get("operating_system"),
        ))
        count += 1
    await db.commit()
    logger.info("  → %d usage logs", count)

async def seed_notifications(db: AsyncSession, emp_map: dict[str, str]):
    rows = _read_csv("notifications.csv")
    count = 0
    for row in rows:
        emp_id = emp_map.get(row.get("user_id", ""))
        db.add(Notification(
            id=str(uuid.uuid4()),
            user_id=emp_id,
            title=row.get("title", "Notification"),
            message=row.get("message", ""),
            category="system",
            priority=row.get("severity", "medium") if row.get("severity") in ("low","medium","high","critical") else "medium",
            status="read" if _bool(row.get("is_read", "FALSE")) else "unread",
        ))
        count += 1
    await db.commit()
    logger.info("  → %d notifications", count)

async def main():
    logger.info("Creating tables if needed...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        existing = await db.execute(select(Company).limit(1))
        if existing.scalar_one_or_none():
            logger.warning("Data already exists — skipping import. Delete test.db to re-import.")
            return

        logger.info("Seeding companies..."); cm = await seed_companies(db)
        logger.info("Seeding departments..."); dm = await seed_departments(db, cm)
        logger.info("Seeding asset categories..."); acm = await seed_asset_categories(db)
        logger.info("Seeding employees..."); em = await seed_employees(db, cm, dm)
        logger.info("Seeding vendors..."); vm = await seed_vendors(db)
        logger.info("Seeding locations..."); lm = await seed_locations(db, cm)
        logger.info("Seeding software categories..."); scm = await seed_software_categories(db)
        logger.info("Seeding software..."); swm = await seed_software(db, vm, scm)
        logger.info("Seeding licenses..."); await seed_licenses(db, swm)
        logger.info("Seeding assets..."); await seed_assets(db, acm, em)
        logger.info("Seeding usage logs..."); await seed_usage_logs(db, em, swm, dm)
        logger.info("Seeding notifications..."); await seed_notifications(db, em)
        logger.info("DONE — all datasets imported.")

if __name__ == "__main__":
    asyncio.run(main())
