"""
AssetOptima — Enterprise Dataset Generator
Generates realistic CSV datasets for development, testing, and AI/ML training.
"""

import csv
import hashlib
import random
import uuid
from datetime import datetime, timedelta, date
from collections import defaultdict

random.seed(42)

OUTPUT_DIR = r"D:\SB4_University\Artificial Intelligence\UAS_Nayla\AssetOptima\datasets\raw"

# ──────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ──────────────────────────────────────────────────────────────────────────────

COMPANIES = [
    ("PT Global Solusi Teknologi", "GST", "Enterprise IT Solutions"),
    ("PT Bank Digital Nusantara", "BDN", "Digital Banking"),
    ("PT Ecommerce Maju Bersama", "EMB", "E-commerce Platform"),
    ("PT Rumah Sakit Sejahtera", "RSS", "Healthcare Provider"),
    ("PT Universitas Harapan Bangsa", "UHB", "Education Institution"),
    ("PT Manufaktur Indonesia Jaya", "MIJ", "Manufacturing"),
    ("PT Asuransi Jiwa Kita", "AJK", "Insurance"),
    ("PT Logistik Express Nusantara", "LEN", "Logistics & Supply Chain"),
    ("PT Media Digital Kreatif", "MDK", "Media & Entertainment"),
    ("PT Energi Terbarukan Mandiri", "ETM", "Renewable Energy"),
]

DEPARTMENTS_DATA = [
    ("Information Technology", "IT"),
    ("Finance & Accounting", "FIN"),
    ("Human Resources", "HR"),
    ("Marketing", "MKT"),
    ("Sales", "SALES"),
    ("Legal & Compliance", "LEGAL"),
    ("Operations", "OPS"),
    ("Procurement", "PROC"),
    ("Customer Support", "SUPPORT"),
    ("Executive Management", "EXEC"),
]

# Indonesian full names (first + last)
FIRST_NAMES_MALE = [
    "Agus", "Bambang", "Cahyo", "Dede", "Eko", "Fajar", "Gunawan", "Hendra",
    "Indra", "Joko", "Kadek", "Lutfi", "Mulyono", "Nugroho", "Oka", "Putu",
    "Rudi", "Slamet", "Teguh", "Ujang", "Wahyu", "Yusuf", "Zainal", "Adi",
    "Bayu", "Candra", "Dimas", "Edi", "Fitrianto", "Gilang", "Heru", "Irfan",
    "Jatmiko", "Kurniawan", "Lukman", "Mahmud", "Nanda", "Pramono", "Rahmat",
    "Surya"
]

FIRST_NAMES_FEMALE = [
    "Ani", "Bunga", "Citra", "Dewi", "Endah", "Fitri", "Gita", "Hesti",
    "Indah", "Juwita", "Kartika", "Lestari", "Mega", "Nia", "Olivia",
    "Puspita", "Ratna", "Sari", "Tina", "Utami", "Vina", "Wulan", "Yuli",
    "Zahra", "Ayu", "Bella", "Cynthia", "Dian", "Elok", "Farah", "Gadis",
    "Hana", "Ika", "Jenny", "Kiki", "Laras", "Nurul", "Putri", "Rina", "Silvi"
]

LAST_NAMES = [
    "Santoso", "Wijaya", "Kusuma", "Pratama", "Wibowo", "Hartono", "Siregar",
    "Nasution", "Saragih", "Simanjuntak", "Saputra", "Gunawan", "Susanto",
    "Hidayat", "Nugroho", "Halim", "Lie", "Tan", "Lim", "Ong", "Salim",
    "Tjahyadi", "Sugiharto", "Purnomo", "Setiawan", "Hermawan", "Atmaja",
    "Dwiyanto", "Winarso", "Mulyadi", "Suharto", "Irawan", "Handoko",
    "Supriyadi", "Sudrajat", "Haryanto", "Maryono", "Susilo", "Prasetyo", "Yulianto"
]

POSITIONS_BY_DEPT = {
    "IT": [
        "IT Manager", "System Administrator", "Network Engineer", "Security Analyst",
        "Database Administrator", "Helpdesk Support", "DevOps Engineer", "IT Director",
        "Cloud Architect", "IT Support Specialist"
    ],
    "FIN": [
        "Finance Manager", "Accountant", "Financial Analyst", "Tax Specialist",
        "Treasury Analyst", "Internal Auditor", "CFO", "Payroll Specialist",
        "Accounts Payable", "Accounts Receivable"
    ],
    "HR": [
        "HR Manager", "HR Generalist", "Recruitment Specialist", "Training Coordinator",
        "Compensation Analyst", "HR Information System Analyst", "HR Director",
        "Employee Relations Specialist", "Benefits Administrator", "HR Assistant"
    ],
    "MKT": [
        "Marketing Manager", "Digital Marketing Specialist", "Content Writer",
        "SEO Specialist", "Social Media Manager", "Brand Strategist", "CMO",
        "Marketing Analyst", "Graphic Designer", "Campaign Coordinator"
    ],
    "SALES": [
        "Sales Manager", "Account Executive", "Sales Representative",
        "Business Development", "Key Account Manager", "Sales Analyst",
        "VP of Sales", "Inside Sales Specialist", "Sales Coordinator",
        "Regional Sales Manager"
    ],
    "LEGAL": [
        "Legal Counsel", "Compliance Officer", "Contract Specialist",
        "Legal Assistant", "General Counsel", "Risk Analyst",
        "Regulatory Affairs Specialist", "Corporate Secretary", "Paralegal",
        "Policy Analyst"
    ],
    "OPS": [
        "Operations Manager", "Supply Chain Analyst", "Logistics Coordinator",
        "Quality Assurance Specialist", "Process Improvement Lead", "COO",
        "Facility Manager", "Operations Analyst", "Project Manager",
        "Vendor Coordinator"
    ],
    "PROC": [
        "Procurement Manager", "Purchasing Specialist", "Vendor Manager",
        "Sourcing Analyst", "Contract Administrator", "Procurement Director",
        "Strategic Sourcing Lead", "Buyer", "Category Manager",
        "Supply Chain Planner"
    ],
    "SUPPORT": [
        "Customer Service Manager", "Support Agent", "Technical Support",
        "Customer Success Manager", "Support Analyst", "Call Center Lead",
        "Client Relations Specialist", "Support Engineer", "Escalation Specialist",
        "Quality Monitoring Analyst"
    ],
    "EXEC": [
        "CEO", "CTO", "CIO", "COO", "CFO", "CMO", "VP of Engineering",
        "VP of Operations", "Board Secretary", "Executive Assistant"
    ],
}

SOFTWARE_CATALOG = [
    ("Microsoft 365 Business Premium", "Microsoft", "per_seat", True, 22.00, 264.00),
    ("Adobe Creative Cloud All Apps", "Adobe", "per_seat", True, 54.99, 659.88),
    ("Slack Enterprise Grid", "Slack", "per_user", True, 15.00, 180.00),
    ("Zoom Business", "Zoom Video Communications", "per_user", True, 19.99, 239.88),
    ("Notion Team Plan", "Notion Labs", "per_user", True, 10.00, 120.00),
    ("GitHub Enterprise", "GitHub/Microsoft", "per_user", True, 21.00, 252.00),
    ("Jira Software Cloud", "Atlassian", "per_user", True, 7.75, 93.00),
    ("Confluence Cloud", "Atlassian", "per_user", True, 6.00, 72.00),
    ("AutoCAD LT", "Autodesk", "per_seat", False, 50.00, 600.00),
    ("Figma Professional", "Figma", "per_seat", True, 12.00, 144.00),
    ("Salesforce Sales Cloud", "Salesforce", "per_user", True, 75.00, 900.00),
    ("HubSpot Enterprise", "HubSpot", "per_user", True, 50.00, 600.00),
    ("Atlassian Bitbucket", "Atlassian", "per_user", True, 6.00, 72.00),
    ("Datadog Infrastructure", "Datadog", "per_host", True, 15.00, 180.00),
    ("AWS Business Support", "Amazon Web Services", "enterprise", True, 100.00, 1200.00),
    ("Tableau Creator", "Salesforce/Tableau", "per_user", True, 70.00, 840.00),
    ("Power BI Pro", "Microsoft", "per_user", True, 10.00, 120.00),
    ("Monday.com Enterprise", "Monday.com", "per_user", True, 22.00, 264.00),
    ("Zendesk Suite", "Zendesk", "per_user", True, 55.00, 660.00),
    ("DocuSign Enterprise", "DocuSign", "per_user", True, 40.00, 480.00),
]

ASSET_CATEGORIES_DATA = [
    ("Laptop", True, 36),
    ("Desktop", True, 48),
    ("Monitor", True, 60),
    ("Smartphone", True, 24),
    ("Printer", True, 60),
    ("Server", True, 60),
    ("Network Switch", True, 84),
    ("Router", True, 60),
    ("Tablet", True, 36),
    ("Peripheral", False, None),
]

# Laptop models
LAPTOP_BRANDS_MODELS = [
    ("Dell", "Latitude 5540"),
    ("Dell", "XPS 15 9530"),
    ("HP", "EliteBook 840 G10"),
    ("HP", "ProBook 450 G10"),
    ("Lenovo", "ThinkPad X1 Carbon Gen 11"),
    ("Lenovo", "ThinkPad T14s Gen 4"),
    ("Apple", "MacBook Pro 14 M3"),
    ("Apple", "MacBook Air 15 M3"),
    ("Microsoft", "Surface Laptop 5"),
    ("ASUS", "ZenBook 14 OLED"),
]
DESKTOP_BRANDS_MODELS = [
    ("Dell", "OptiPlex 7000 Tower"),
    ("HP", "EliteDesk 800 G9"),
    ("Lenovo", "ThinkCentre M90s Gen 4"),
    ("Apple", "Mac Mini M2"),
    ("Apple", "Mac Studio M2 Max"),
]
MONITOR_BRANDS_MODELS = [
    ("Dell", "U2723QE 4K USB-C Hub"),
    ("Dell", "P2423DE 24\" 16:9"),
    ("HP", "E27u G5 27\" 4K"),
    ("LG", "27UP850N 27\" 4K"),
    ("Samsung", "S27A800 27\" 4K"),
]
SMARTPHONE_BRANDS_MODELS = [
    ("Apple", "iPhone 15 Pro"),
    ("Apple", "iPhone 15"),
    ("Apple", "iPhone 14"),
    ("Samsung", "Galaxy S24 Ultra"),
    ("Samsung", "Galaxy S24"),
    ("Google", "Pixel 8 Pro"),
    ("Xiaomi", "13T Pro"),
]
PRINTER_BRANDS_MODELS = [
    ("HP", "LaserJet Pro M404dn"),
    ("HP", "LaserJet Enterprise M507"),
    ("Brother", "HL-L2370DW"),
    ("Epson", "WorkForce Pro WF-7820"),
    ("Canon", "imageRUNNER 2630i"),
]
SERVER_BRANDS_MODELS = [
    ("Dell", "PowerEdge R750xs"),
    ("Dell", "PowerEdge R650"),
    ("HP", "ProLiant DL380 Gen11"),
    ("Lenovo", "ThinkSystem SR650 V3"),
    ("Supermicro", "SYS-420GP"),
]
NETWORK_BRANDS_MODELS = [
    ("Cisco", "Catalyst 9200-48P"),
    ("Cisco", "Catalyst 9300-48P"),
    ("Ubiquiti", "UniFi Switch Pro 48"),
    ("MikroTik", "CRS326-24G-2S+RM"),
    ("Juniper", "EX3400-48P"),
]
ROUTER_BRANDS_MODELS = [
    ("Cisco", "ISR 4321"),
    ("Cisco", "ISR 1100-8P"),
    ("Ubiquiti", "UniFi Dream Machine SE"),
    ("MikroTik", "RB4011iGS+RM"),
    ("Fortinet", "FortiGate 60F"),
]
TABLET_BRANDS_MODELS = [
    ("Apple", "iPad Pro 12.9 M2"),
    ("Apple", "iPad Air M1"),
    ("Samsung", "Galaxy Tab S9 Ultra"),
    ("Samsung", "Galaxy Tab S9 FE"),
    ("Microsoft", "Surface Pro 9"),
]
PERIPHERAL_BRANDS_MODELS = [
    ("Logitech", "MX Master 3S Mouse"),
    ("Logitech", "MX Keys Keyboard"),
    ("Logitech", "C922 Pro Webcam"),
    ("Jabra", "Evolve2 65 Headset"),
    ("Poly", "Voyager 5200 Headset"),
]

CATEGORY_ASSETS = {
    "Laptop": LAPTOP_BRANDS_MODELS,
    "Desktop": DESKTOP_BRANDS_MODELS,
    "Monitor": MONITOR_BRANDS_MODELS,
    "Smartphone": SMARTPHONE_BRANDS_MODELS,
    "Printer": PRINTER_BRANDS_MODELS,
    "Server": SERVER_BRANDS_MODELS,
    "Network Switch": NETWORK_BRANDS_MODELS,
    "Router": ROUTER_BRANDS_MODELS,
    "Tablet": TABLET_BRANDS_MODELS,
    "Peripheral": PERIPHERAL_BRANDS_MODELS,
}

CATEGORY_PRICE_RANGES = {
    "Laptop": (1200, 3500),
    "Desktop": (800, 3000),
    "Monitor": (300, 1200),
    "Smartphone": (600, 1500),
    "Printer": (200, 2000),
    "Server": (3000, 15000),
    "Network Switch": (500, 4000),
    "Router": (300, 2500),
    "Tablet": (400, 1200),
    "Peripheral": (50, 300),
}

STATUSES = ["available", "assigned", "maintenance", "retired", "lost", "stolen"]
STATUS_WEIGHTS = [0.35, 0.45, 0.10, 0.07, 0.02, 0.01]

CONDITIONS = ["new", "good", "fair", "poor", "damaged", "repairing"]
CONDITION_WEIGHTS = [0.15, 0.50, 0.20, 0.10, 0.03, 0.02]

COMPANY_ID = "comp-001"

# ──────────────────────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def uuid_from_int(n: int) -> str:
    """Deterministic UUID from integer."""
    return str(uuid.UUID(hashlib.md5(str(n).encode()).hexdigest()))

def random_date(start: date, end: date) -> date:
    return start + timedelta(days=random.randint(0, (end - start).days))

def write_csv(filename: str, fieldnames: list, rows: list):
    path = f"{OUTPUT_DIR}/{filename}"
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  ✓ {filename} ({len(rows)} rows)")

def pick_weighted(items, weights):
    return random.choices(items, weights=weights, k=1)[0]


# ══════════════════════════════════════════════════════════════════════════════
# 1. COMPANIES
# ══════════════════════════════════════════════════════════════════════════════

def gen_companies():
    rows = []
    for i, (name, code, desc) in enumerate(COMPANIES, 1):
        rows.append({
            "company_id": f"comp-{i:03d}",
            "name": name,
            "code": code,
            "description": desc,
            "tax_id": f"{random.randint(10,99)}.{random.randint(100,999)}.{random.randint(100,999)}.{random.randint(1,9)}-{random.randint(100,999)}.{random.randint(10,99)}",
            "phone": f"+62-21-{random.randint(1000000,9999999)}",
            "email": f"info@{code.lower()}.co.id",
            "address": f"Jl. {random.choice(['Sudirman','Thamrin','Kuningan','Gatot Subroto','Rasuna Said'])} No. {random.randint(1,500)}, Jakarta",
            "is_active": "TRUE",
            "max_employees": random.choice([100, 250, 500, 1000, 2000]),
            "subscription_plan": random.choice(["starter", "business", "enterprise"]),
            "created_at": f"2024-01-{random.randint(1,31):02d} 09:00:00+07",
        })
    return rows


# ══════════════════════════════════════════════════════════════════════════════
# 2. DEPARTMENTS
# ══════════════════════════════════════════════════════════════════════════════

def gen_departments():
    rows = []
    for i, (name, code) in enumerate(DEPARTMENTS_DATA, 1):
        rows.append({
            "department_id": f"dept-{i:02d}",
            "company_id": "comp-001",
            "name": name,
            "code": code,
            "cost_center": f"CC-{code}-{random.randint(10,99)}",
            "is_active": "TRUE",
        })
    return rows


# ══════════════════════════════════════════════════════════════════════════════
# 3. EMPLOYEES (100 with Indonesian names)
# ══════════════════════════════════════════════════════════════════════════════

def gen_employees():
    rows = []
    # Assign rough distribution of employees to departments
    dept_employee_counts = {
        "dept-01": 20,  # IT
        "dept-02": 12,  # Finance
        "dept-03": 8,   # HR
        "dept-04": 10,  # Marketing
        "dept-05": 10,  # Sales
        "dept-06": 5,   # Legal
        "dept-07": 12,  # Ops
        "dept-08": 6,   # Procurement
        "dept-09": 10,  # Support
        "dept-10": 7,   # Exec
    }
    used_names = set()
    emp_id = 1

    for dept_id, count in dept_employee_counts.items():
        dept_name = DEPARTMENTS_DATA[int(dept_id.split("-")[1]) - 1][0]
        positions = POSITIONS_BY_DEPT[dept_name]
        for _ in range(count):
            is_male = random.random() > 0.5
            while True:
                first = random.choice(FIRST_NAMES_MALE if is_male else FIRST_NAMES_FEMALE)
                last = random.choice(LAST_NAMES)
                full_name = f"{first} {last}"
                if full_name not in used_names:
                    used_names.add(full_name)
                    break

            join = random_date(date(2019, 1, 1), date(2025, 12, 1))
            status = random.choices(
                ["active", "active", "active", "notice", "offboarding", "inactive"],
                weights=[0.70, 0.10, 0.05, 0.05, 0.05, 0.05],
                k=1
            )[0]

            resign = ""
            if status in ("inactive",):
                resign = str(random_date(join, date(2026, 3, 1)))

            email = f"{first.lower()}.{last.lower()}@company.co.id"

            rows.append({
                "employee_id": f"emp-{emp_id:03d}",
                "company_id": "comp-001",
                "department_id": dept_id,
                "full_name": full_name,
                "first_name": first,
                "last_name": last,
                "email": email,
                "phone": f"+62-8{random.randint(11,99)}-{random.randint(1000,9999)}-{random.randint(1000,9999)}",
                "position": random.choice(positions),
                "department_name": dept_name,
                "employment_status": status,
                "join_date": str(join),
                "resign_date": resign,
            })
            emp_id += 1

    # Assign managers — first employee in each dept is manager
    dept_managers = {}
    for r in rows:
        d = r["department_id"]
        if d not in dept_managers:
            dept_managers[d] = r["employee_id"]
        r["manager_id"] = dept_managers[d]

    # For rows that are the manager themselves, set manager to exec or null
    exec_employees = [r for r in rows if r["department_id"] == "dept-10"]
    for d, mgr_id in dept_managers.items():
        if d == "dept-10":
            continue
        for r in rows:
            if r["employee_id"] == mgr_id and r["department_id"] != "dept-10":
                # Assign to exec
                if exec_employees:
                    r["manager_id"] = exec_employees[0]["employee_id"]

    return rows


# ══════════════════════════════════════════════════════════════════════════════
# 4. ASSET CATEGORIES
# ══════════════════════════════════════════════════════════════════════════════

def gen_asset_categories():
    rows = []
    for i, (name, depr, months) in enumerate(ASSET_CATEGORIES_DATA, 1):
        rows.append({
            "category_id": f"cat-{i:02d}",
            "company_id": "comp-001",
            "name": name,
            "code": name.upper().replace(" ", "_")[:10],
            "is_depreciable": "TRUE" if depr else "FALSE",
            "useful_life_months": str(months) if months else "",
        })
    return rows


# ══════════════════════════════════════════════════════════════════════════════
# 5. ASSETS (500)
# ══════════════════════════════════════════════════════════════════════════════

def gen_assets(employees):
    rows = []
    employee_ids = [e["employee_id"] for e in employees if e["employment_status"] == "active"]

    assigned_employees = random.choices(employee_ids, k=220)
    assigned_idx = 0

    for i in range(1, 501):
        cat_name = random.choices(
            list(CATEGORY_ASSETS.keys()),
            weights=[0.30, 0.08, 0.15, 0.12, 0.03, 0.05, 0.05, 0.05, 0.07, 0.10],
            k=1
        )[0]
        cat_id = f"cat-{list(ASSET_CATEGORIES_DATA).index([c for c in ASSET_CATEGORIES_DATA if c[0]==cat_name][0])+1:02d}"
        brand, model = random.choice(CATEGORY_ASSETS[cat_name])
        price_range = CATEGORY_PRICE_RANGES[cat_name]
        price = round(random.uniform(price_range[0], price_range[1]), 2)

        status = pick_weighted(STATUSES, STATUS_WEIGHTS)
        condition = pick_weighted(CONDITIONS, CONDITION_WEIGHTS)

        purchase = random_date(date(2020, 1, 1), date(2025, 12, 31))
        warranty = purchase + timedelta(days=random.choice([365, 730, 1095, 1460]))

        serial = f"{brand[:3].upper()}-{cat_name[:4].upper()}-{random.randint(10000,99999)}-{random.randint(1000,9999)}"

        # Assign to employee if 'assigned'
        current_employee = ""
        if status == "assigned" and assigned_idx < len(assigned_employees):
            current_employee = assigned_employees[assigned_idx]
            assigned_idx += 1
            if random.random() > 0.5:
                assigned_idx += 1  # skip some to create unassigned assets

        row = {
            "asset_id": f"ast-{i:05d}",
            "company_id": "comp-001",
            "category_id": cat_id,
            "category_name": cat_name,
            "asset_tag": f"AST-{i:05d}",
            "brand": brand,
            "model": model,
            "serial_number": serial,
            "purchase_date": str(purchase),
            "purchase_price": f"{price:.2f}",
            "warranty_expiry": str(warranty),
            "status": status,
            "condition": condition,
            "current_employee_id": current_employee,
            "location": random.choice([
                "Jakarta HQ - Floor 1", "Jakarta HQ - Floor 2",
                "Jakarta HQ - Floor 3", "Jakarta HQ - Floor 4",
                "Jakarta HQ - Floor 5", "Warehouse - Jakarta",
                "Warehouse - Bandung", "Data Center - Jakarta",
                "Remote - WFH", "Branch - Surabaya",
            ]),
            "notes": "",
        }
        rows.append(row)

    return rows


# ══════════════════════════════════════════════════════════════════════════════
# 6. SOFTWARE CATALOG
# ══════════════════════════════════════════════════════════════════════════════

def gen_software_catalog():
    rows = []
    for i, (name, vendor, model, is_cloud, monthly, annual) in enumerate(SOFTWARE_CATALOG, 1):
        rows.append({
            "software_id": f"sw-{i:02d}",
            "company_id": "comp-001",
            "name": name,
            "vendor": vendor,
            "license_model": model,
            "is_cloud": "TRUE" if is_cloud else "FALSE",
            "monthly_cost_per_seat": f"{monthly:.2f}",
            "annual_cost_per_seat": f"{annual:.2f}",
            "category": random.choice([
                "Productivity", "Creative", "Communication",
                "Dev Tools", "CRM", "Analytics", "Project Management",
            ]),
        })
    return rows


# ══════════════════════════════════════════════════════════════════════════════
# 7. LICENSES (one license block per software)
# ══════════════════════════════════════════════════════════════════════════════

def gen_licenses():
    rows = []
    for i, (name, vendor, model, is_cloud, monthly, annual) in enumerate(SOFTWARE_CATALOG, 1):
        total = random.choice([10, 15, 20, 25, 30, 40, 50, 60, 75, 100])
        used = random.randint(1, total)
        rows.append({
            "license_id": f"lic-{i:02d}",
            "company_id": "comp-001",
            "software_id": f"sw-{i:02d}",
            "software_name": name,
            "license_type": "subscription" if is_cloud else "perpetual",
            "total_licenses": str(total),
            "used_licenses": str(used),
            "available_licenses": str(total - used),
            "renewal_date": str(random_date(date(2026, 1, 1), date(2026, 12, 31))),
            "monthly_cost": f"{monthly:.2f}",
            "annual_cost": f"{annual:.2f}",
            "total_monthly_cost": f"{monthly * total:.2f}",
            "total_annual_cost": f"{annual * total:.2f}",
            "status": "active",
        })
    return rows


# ══════════════════════════════════════════════════════════════════════════════
# 8. SOFTWARE USAGE LOGS (20,000 records)
# ── Creates realistic patterns for dormant detection
# ── Some users NEVER login (dormant accounts)
# ── Some users login daily (power users)
# ── Some users login weekly/occasionally
# ══════════════════════════════════════════════════════════════════════════════

def gen_software_usage_logs(employees, software_catalog):
    rows = []

    # Map employees to software based on department relevance
    dept_software_map = {
        "IT": [1, 3, 4, 6, 7, 8, 10, 14, 15, 16, 17, 18],
        "FIN": [1, 2, 11, 12, 16, 17, 19],
        "HR": [1, 5, 11, 12, 18, 19],
        "MKT": [1, 2, 4, 5, 9, 10, 11, 12, 18],
        "SALES": [1, 3, 4, 11, 12, 18, 19],
        "LEGAL": [1, 19, 20],
        "OPS": [1, 4, 5, 7, 8, 11, 15, 18, 19],
        "PROC": [1, 5, 11, 18, 19],
        "SUPPORT": [1, 3, 4, 7, 8, 11, 19],
        "EXEC": [1, 3, 4, 5, 11, 12, 13, 14, 15],
    }

    employee_assignments = defaultdict(list)

    for emp in employees:
        dept = emp["department_name"]
        sw_indices = dept_software_map.get(dept, [1, 3, 4])
        # Not all employees in a dept get all software
        n_sw = random.randint(2, min(len(sw_indices), 5))
        assigned_sw = random.sample(sw_indices, n_sw)
        for sw_idx in assigned_sw:
            employee_assignments[emp["employee_id"]].append(sw_idx)

    # Usage patterns per employee-software pair
    # Define usage patterns:
    #   dormant:     never logs in (0% chance)
    #   very_light:  logs in 1-2 days per month
    #   light:       logs in 1 day per week
    #   regular:     3-4 days per week
    #   heavy:       5-7 days per week
    PATTERNS = ["dormant", "very_light", "light", "regular", "heavy"]
    PATTERN_WEIGHTS = [0.12, 0.15, 0.25, 0.33, 0.15]  # 12% dormant

    start_date = date(2025, 7, 1)
    end_date = date(2026, 6, 30)
    date_range = (end_date - start_date).days

    DEVICES = ["Windows Laptop", "MacBook Pro", "Windows Desktop", "iPhone",
               "Android Phone", "iPad", "Linux Workstation"]
    OS = ["Windows 11", "macOS 14 Sonoma", "macOS 15 Sequoia",
          "iOS 17", "Android 14", "Ubuntu 22.04", "Windows 10"]
    COUNTRIES = ["Indonesia", "Indonesia", "Indonesia", "Singapore",
                 "Malaysia", "United States", "Australia"]
    IPS = [f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}" for _ in range(20)]
    STATUSES_LOGIN = ["Success", "Success", "Success", "Success", "Failed", "Failed"]

    row_id = 1

    for emp in employees:
        eid = emp["employee_id"]
        if eid not in employee_assignments:
            continue

        for sw_idx in employee_assignments[eid]:
            pattern = pick_weighted(PATTERNS, PATTERN_WEIGHTS)
            sw_id = f"sw-{sw_idx:02d}"

            if pattern == "dormant":
                # DORMANT: assigned but NEVER logs in — zero records
                continue

            # Determine login frequency
            if pattern == "very_light":
                days_per_month = random.randint(1, 2)
            elif pattern == "light":
                days_per_month = random.randint(4, 8)
            elif pattern == "regular":
                days_per_month = random.randint(12, 20)
            else:  # heavy
                days_per_month = random.randint(22, 28)

            # Generate sessions across the year
            current = start_date
            while current <= end_date:
                month_days = []
                # Pick random days this month
                month_end = date(current.year, current.month, 1) + timedelta(days=32)
                month_end = month_end.replace(day=1) - timedelta(days=1)
                if month_end > end_date:
                    month_end = end_date

                valid_days = (month_end - current).days + 1
                if valid_days <= 0:
                    break

                n_logins_this_month = min(days_per_month, valid_days)
                login_days = sorted(random.sample(range(valid_days), n_logins_this_month))

                for day_offset in login_days:
                    login_date = current + timedelta(days=day_offset)
                    if login_date > end_date:
                        break

                    login_hour = random.randint(7, 18)
                    login_minute = random.randint(0, 59)
                    duration_min = random.randint(15, 480)
                    logout_hour = login_hour + duration_min // 60
                    logout_minute = login_minute + duration_min % 60

                    if logout_hour >= 24:
                        logout_hour = 23
                        logout_minute = 59

                    login_status = random.choices(STATUSES_LOGIN, weights=[0.90, 0.03, 0.03, 0.02, 0.01, 0.01], k=1)[0]

                    rows.append({
                        "log_id": str(row_id),
                        "employee_id": eid,
                        "employee_name": emp["full_name"],
                        "employee_email": emp["email"],
                        "department": emp["department_name"],
                        "software_id": sw_id,
                        "software_name": SOFTWARE_CATALOG[sw_idx - 1][0],
                        "login_date": str(login_date),
                        "login_time": f"{login_hour:02d}:{login_minute:02d}:00",
                        "logout_time": f"{logout_hour:02d}:{logout_minute:02d}:00",
                        "session_duration_minutes": str(duration_min),
                        "device": random.choice(DEVICES),
                        "ip_address": random.choice(IPS),
                        "operating_system": random.choice(OS),
                        "country": random.choice(COUNTRIES),
                        "login_status": login_status,
                    })
                    row_id += 1
                    if row_id > 20000:
                        return rows[:20000]

                current = date(current.year, current.month + 1, 1) if current.month < 12 else date(current.year + 1, 1, 1)

    return rows[:20000]


# ══════════════════════════════════════════════════════════════════════════════
# 9. QR CODES
# ══════════════════════════════════════════════════════════════════════════════

def gen_qr_codes(assets):
    rows = []
    for a in assets[:]:
        code = hashlib.sha256(f"assetop-{a['asset_tag']}-{a['serial_number']}".encode()).hexdigest()[:24]
        rows.append({
            "qr_id": f"qr-{a['asset_id'].split('-')[1]}",
            "asset_id": a["asset_id"],
            "asset_tag": a["asset_tag"],
            "qr_value": code.upper(),
            "is_printed": "TRUE" if random.random() > 0.15 else "FALSE",
            "scan_count": str(random.randint(0, 50)),
        })
    return rows


# ══════════════════════════════════════════════════════════════════════════════
# 10. PREDICTION HISTORY
# ══════════════════════════════════════════════════════════════════════════════

def gen_predictions(software_catalog):
    rows = []
    for sw in software_catalog:
        sw_id = sw["software_id"]
        sw_name = sw["name"]
        for month_offset in range(6):
            pred_date = date(2026, 1, 1) + timedelta(days=month_offset * 30)
            base = random.randint(15, 50)
            predicted = base + random.randint(-3, 3)
            actual = predicted + random.randint(-5, 5)
            rows.append({
                "prediction_id": f"pred-{sw_id.split('-')[1]}-{month_offset+1:02d}",
                "company_id": "comp-001",
                "software_id": sw_id,
                "software_name": sw_name,
                "prediction_type": "license_forecast",
                "model_name": "Prophet-v2",
                "model_version": "2.3.1",
                "prediction_date": str(pred_date),
                "predicted_license_demand": str(predicted),
                "actual_license_demand": str(actual),
                "confidence_score": f"{random.uniform(0.75, 0.98):.4f}",
                "is_anomaly": "FALSE",
            })

    # Add anomaly predictions (dormant detection)
    for sw in random.sample(software_catalog, 5):
        sw_id = sw["software_id"]
        sw_name = sw["name"]
        for _ in range(3):
            pred_date = random_date(date(2026, 1, 1), date(2026, 6, 30))
            dormant_count = random.randint(2, 12)
            rows.append({
                "prediction_id": f"pred-anom-{sw_id.split('-')[1]}-{random.randint(1,9)}",
                "company_id": "comp-001",
                "software_id": sw_id,
                "software_name": sw_name,
                "prediction_type": "dormant_detection",
                "model_name": "IsolationForest-v1",
                "model_version": "1.0.2",
                "prediction_date": str(pred_date),
                "predicted_license_demand": str(dormant_count),
                "actual_license_demand": str(dormant_count + random.randint(-2, 2)),
                "confidence_score": f"{random.uniform(0.82, 0.99):.4f}",
                "is_anomaly": "TRUE",
            })
    return rows


# ══════════════════════════════════════════════════════════════════════════════
# 11. RECOMMENDATIONS
# ══════════════════════════════════════════════════════════════════════════════

def gen_recommendations(predictions):
    rows = []
    active_preds = [p for p in predictions if p["prediction_type"] == "license_forecast"]
    for p in active_preds:
        if random.random() > 0.4:
            continue
        reduction = random.randint(1, 8)
        savings = reduction * random.uniform(10, 75)
        rows.append({
            "recommendation_id": f"reco-{p['prediction_id']}",
            "company_id": "comp-001",
            "prediction_id": p["prediction_id"],
            "software_name": p["software_name"],
            "recommendation_type": random.choice(["license_reduce", "revoke_dormant", "cost_saving"]),
            "title": f"Reduce {p['software_name']} licenses by {reduction}",
            "description": f"AI detected {reduction} dormant seats in {p['software_name']}. "
                           f"Recommended action: revoke and save estimated ${savings:.0f}/month.",
            "priority": random.choice(["low", "medium", "high"]),
            "estimated_monthly_savings": f"{savings:.2f}",
            "status": random.choice(["pending", "applied", "dismissed"]),
            "created_at": f"{p['prediction_date']} 08:00:00+07",
        })

    # Anomaly-based recommendations
    anom_preds = [p for p in predictions if p["prediction_type"] == "dormant_detection"]
    for p in anom_preds:
        savings = random.uniform(100, 500)
        rows.append({
            "recommendation_id": f"reco-anom-{p['prediction_id']}",
            "company_id": "comp-001",
            "prediction_id": p["prediction_id"],
            "software_name": p["software_name"],
            "recommendation_type": "revoke_dormant",
            "title": f"Dormant accounts detected in {p['software_name']}",
            "description": f"Isolation Forest flagged {p['predicted_license_demand']} dormant users. "
                           f"Estimated annual savings: ${savings:.0f}.",
            "priority": "high",
            "estimated_monthly_savings": f"{savings:.2f}",
            "status": "pending",
            "created_at": f"{p['prediction_date']} 09:30:00+07",
        })
    return rows


# ══════════════════════════════════════════════════════════════════════════════
# 12. AI CHAT HISTORY (RAG conversations)
# ══════════════════════════════════════════════════════════════════════════════

def gen_ai_chat_history(employees):
    questions = [
        "What is the offboarding procedure for employees?",
        "How do I reset my laptop password?",
        "What software is available for video editing?",
        "Show me the IT asset policy for laptop assignments.",
        "How many laptops are currently assigned to Engineering?",
        "What is the SLA for helpdesk ticket resolution?",
        "Can you summarize the company's security policy?",
        "Which employees have Adobe Creative Cloud licenses?",
        "What is the process for requesting new software?",
        "How do I connect to the VPN from home?",
        "What are the costs of our Slack subscription?",
        "Show me assets that are out of warranty.",
        "What is the company policy on software installation?",
        "How do I report a lost company laptop?",
        "What is the headcount trend for Q2 2026?",
    ]
    rows = []
    users = [e for e in employees if e["employment_status"] == "active"]
    session_groups = defaultdict(list)
    for i, u in enumerate(users[:30]):
        session_id = f"sess-{i:04d}"
        n_messages = random.randint(2, 6)
        for j in range(n_messages):
            q = random.choice(questions)
            tokens_q = len(q.split()) * random.randint(2, 5)
            tokens_a = random.randint(50, 300)
            rows.append({
                "chat_id": f"chat-{i:04d}-{j:02d}",
                "company_id": "comp-001",
                "user_id": u["employee_id"],
                "user_name": u["full_name"],
                "session_id": session_id,
                "role": "user" if j % 2 == 0 else "assistant",
                "message": q if j % 2 == 0 else f"Based on the retrieved documents, here is the answer to your question about '{q.split('?')[0]}': [Detailed answer with {random.randint(3,8)} bullet points]",
                "tokens_used": str(tokens_q if j % 2 == 0 else tokens_a),
                "model_used": "gpt-4o" if j % 2 == 1 else "",
                "retrieved_documents": str(random.randint(1, 5)) if j % 2 == 1 else "",
                "feedback_score": str(random.randint(3, 5)) if j % 2 == 1 and random.random() > 0.5 else "",
                "created_at": f"2026-0{random.randint(1,6):01d}-{random.randint(1,28):02d} {random.randint(8,17):02d}:{random.randint(0,59):02d}:00+07",
            })
        if len(rows) >= 250:
            break

    return rows[:250]


# ══════════════════════════════════════════════════════════════════════════════
# 13. AUDIT LOGS
# ══════════════════════════════════════════════════════════════════════════════

def gen_audit_logs(employees):
    actions = [
        "user.login", "user.logout", "asset.create", "asset.update",
        "asset.assign", "asset.return", "license.assign", "license.revoke",
        "employee.create", "employee.update", "employee.offboard",
        "software.create", "license.create", "settings.update",
        "report.generate", "ai.query", "ai.prediction.run",
    ]
    entities = ["asset", "license", "employee", "software", "user", "notification"]
    rows = []
    emp_ids = [e["employee_id"] for e in employees if e["employment_status"] == "active"]

    for i in range(1, 301):
        action = random.choice(actions)
        entity = random.choice(entities) if "login" not in action and "logout" not in action else "user"
        rows.append({
            "audit_id": str(i),
            "company_id": "comp-001",
            "user_id": random.choice(emp_ids),
            "action": action,
            "entity_type": entity,
            "entity_id": f"ref-{random.randint(1,500):05d}",
            "ip_address": f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}",
            "user_agent": random.choice([
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/605",
                "Flutter/3.16 (Mobile; iOS 17.2)",
                "Flutter/3.16 (Mobile; Android 14)",
                "Mozilla/5.0 (X11; Linux x86_64) Firefox/121",
            ]),
            "created_at": f"2026-0{random.randint(1,6):01d}-{random.randint(1,28):02d} {random.randint(0,23):02d}:{random.randint(0,59):02d}:{random.randint(0,59):02d}+07",
        })
    return rows


# ══════════════════════════════════════════════════════════════════════════════
# 14. NOTIFICATIONS
# ══════════════════════════════════════════════════════════════════════════════

def gen_notifications():
    types = [
        ("license_expiry", "warning"),
        ("dormant_account", "warning"),
        ("asset_overdue", "critical"),
        ("offboarding", "info"),
        ("maintenance_due", "info"),
        ("prediction", "info"),
        ("recommendation", "info"),
    ]
    rows = []
    for i in range(1, 101):
        nt, sev = random.choice(types)
        titles = {
            "license_expiry": "Software license expiring soon",
            "dormant_account": "Dormant software accounts detected",
            "asset_overdue": "Asset return is overdue",
            "offboarding": "Employee offboarding in progress",
            "maintenance_due": "Asset maintenance scheduled",
            "prediction": "New AI prediction available",
            "recommendation": "Cost-saving recommendation generated",
        }
        rows.append({
            "notification_id": f"notif-{i:03d}",
            "company_id": "comp-001",
            "user_id": f"emp-{random.randint(1,100):03d}",
            "type": nt,
            "severity": sev,
            "title": titles[nt],
            "message": f"{titles[nt]} — please review and take action.",
            "is_read": "TRUE" if random.random() > 0.5 else "FALSE",
            "reference_type": random.choice(["license", "asset", "employee", "prediction"]),
            "reference_id": f"ref-{random.randint(1,500):03d}",
            "created_at": f"2026-0{random.randint(1,6):01d}-{random.randint(1,28):02d} {random.randint(8,17):02d}:{random.randint(0,59):02d}:00+07",
        })
    return rows


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("🔄 Generating AssetOptima Enterprise Datasets...\n")

    # 1. Companies
    print("[1/14] Companies...")
    companies = gen_companies()
    write_csv("companies.csv",
              ["company_id", "name", "code", "description", "tax_id", "phone",
               "email", "address", "is_active", "max_employees", "subscription_plan",
               "created_at"],
              companies)

    # 2. Departments
    print("[2/14] Departments...")
    departments = gen_departments()
    write_csv("departments.csv",
              ["department_id", "company_id", "name", "code", "cost_center", "is_active"],
              departments)

    # 3. Employees
    print("[3/14] Employees...")
    employees = gen_employees()
    write_csv("employees.csv",
              ["employee_id", "company_id", "department_id", "full_name", "first_name",
               "last_name", "email", "phone", "position", "department_name",
               "employment_status", "join_date", "resign_date", "manager_id"],
              employees)

    # 4. Asset Categories
    print("[4/14] Asset Categories...")
    categories = gen_asset_categories()
    write_csv("asset_categories.csv",
              ["category_id", "company_id", "name", "code", "is_depreciable",
               "useful_life_months"],
              categories)

    # 5. Assets
    print("[5/14] Assets...")
    assets = gen_assets(employees)
    write_csv("assets.csv",
              ["asset_id", "company_id", "category_id", "category_name", "asset_tag",
               "brand", "model", "serial_number", "purchase_date", "purchase_price",
               "warranty_expiry", "status", "condition", "current_employee_id",
               "location", "notes"],
              assets)

    # 6. QR Codes
    print("[6/14] QR Codes...")
    qr_codes = gen_qr_codes(assets)
    write_csv("qr_codes.csv",
              ["qr_id", "asset_id", "asset_tag", "qr_value", "is_printed", "scan_count"],
              qr_codes)

    # 7. Software Catalog
    print("[7/14] Software Catalog...")
    software = gen_software_catalog()
    write_csv("software_catalog.csv",
              ["software_id", "company_id", "name", "vendor", "license_model",
               "is_cloud", "monthly_cost_per_seat", "annual_cost_per_seat", "category"],
              software)

    # 8. Licenses
    print("[8/14] Licenses...")
    licenses = gen_licenses()
    write_csv("licenses.csv",
              ["license_id", "company_id", "software_id", "software_name",
               "license_type", "total_licenses", "used_licenses", "available_licenses",
               "renewal_date", "monthly_cost", "annual_cost",
               "total_monthly_cost", "total_annual_cost", "status"],
              licenses)

    # 9. Software Usage Logs (20,000 records)
    print("[9/14] Software Usage Logs (20,000 records - this may take a moment)...")
    usage_logs = gen_software_usage_logs(employees, software)
    write_csv("software_usage_logs.csv",
              ["log_id", "employee_id", "employee_name", "employee_email",
               "department", "software_id", "software_name", "login_date",
               "login_time", "logout_time", "session_duration_minutes",
               "device", "ip_address", "operating_system", "country",
               "login_status"],
              usage_logs)
    dormant_count = 100 - len(set(r["employee_id"] for r in usage_logs))
    print(f"       (Dormant employees with zero logins: ~{dormant_count})")

    # 10. Predictions
    print("[10/14] AI Predictions...")
    predictions = gen_predictions(software)
    write_csv("prediction_history.csv",
              ["prediction_id", "company_id", "software_id", "software_name",
               "prediction_type", "model_name", "model_version", "prediction_date",
               "predicted_license_demand", "actual_license_demand",
               "confidence_score", "is_anomaly"],
              predictions)

    # 11. Recommendations
    print("[11/14] AI Recommendations...")
    recommendations = gen_recommendations(predictions)
    write_csv("recommendations.csv",
              ["recommendation_id", "company_id", "prediction_id", "software_name",
               "recommendation_type", "title", "description", "priority",
               "estimated_monthly_savings", "status", "created_at"],
              recommendations)

    # 12. AI Chat History
    print("[12/14] AI Chat History...")
    chat = gen_ai_chat_history(employees)
    write_csv("ai_chat_history.csv",
              ["chat_id", "company_id", "user_id", "user_name", "session_id",
               "role", "message", "tokens_used", "model_used",
               "retrieved_documents", "feedback_score", "created_at"],
              chat)

    # 13. Audit Logs
    print("[13/14] Audit Logs...")
    audit = gen_audit_logs(employees)
    write_csv("audit_logs.csv",
              ["audit_id", "company_id", "user_id", "action", "entity_type",
               "entity_id", "ip_address", "user_agent", "created_at"],
              audit)

    # 14. Notifications
    print("[14/14] Notifications...")
    notifs = gen_notifications()
    write_csv("notifications.csv",
              ["notification_id", "company_id", "user_id", "type", "severity",
               "title", "message", "is_read", "reference_type", "reference_id",
               "created_at"],
              notifs)

    print("\n✅ All datasets generated successfully in:")
    print(f"   {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
