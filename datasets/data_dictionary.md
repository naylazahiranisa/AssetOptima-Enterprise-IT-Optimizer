# AssetOptima — Enterprise Data Dictionary

**Version:** 1.0  
**Date:** 2026-07-01  
**Author:** Senior Data Engineer  

---

## Overview

This document describes all datasets generated for the AssetOptima Enterprise IT Asset & License Optimizer. The datasets simulate a production IT environment for a mid-to-large Indonesian enterprise (~100 employees, ~500 assets, ~20 software products).

**Total records across all datasets:** 21,877  
**Primary company:** PT Global Solusi Teknologi (comp-001)

---

## Dataset Inventory

| # | File | Rows | Type | Primary Use |
|---|------|------|------|-------------|
| 1 | `companies.csv` | 10 | Master | Multi-tenant structure |
| 2 | `departments.csv` | 10 | Master | Organizational hierarchy |
| 3 | `employees.csv` | 100 | Master | Employee records |
| 4 | `asset_categories.csv` | 10 | Reference | Asset classification |
| 5 | `assets.csv` | 500 | Master | Physical IT assets |
| 6 | `qr_codes.csv` | 500 | Reference | QR code bindings |
| 7 | `software_catalog.csv` | 20 | Master | Software product catalog |
| 8 | `licenses.csv` | 20 | Transaction | License entitlements |
| 9 | `software_usage_logs.csv` | 20,000 | Transaction | Daily usage records |
| 10 | `prediction_history.csv` | 135 | Transaction | ML model outputs |
| 11 | `recommendations.csv` | 57 | Transaction | AI recommendations |
| 12 | `ai_chat_history.csv` | 115 | Transaction | RAG conversations |
| 13 | `audit_logs.csv` | 300 | Transaction | Compliance trail |
| 14 | `notifications.csv` | 100 | Transaction | System alerts |

---

## 1. companies.csv

| Column | Type | Description |
|--------|------|-------------|
| `company_id` | VARCHAR(10) | Primary key. Format: `comp-NNN` |
| `name` | VARCHAR(100) | Legal company name (Indonesian: PT ...) |
| `code` | VARCHAR(5) | Short tenant code (e.g., GST, BDN) |
| `description` | VARCHAR(100) | Industry sector description |
| `tax_id` | VARCHAR(30) | Indonesian NPWP tax ID |
| `phone` | VARCHAR(30) | Main contact number (+62 format) |
| `email` | VARCHAR(100) | Company info email |
| `address` | VARCHAR(200) | Jakarta-based office address |
| `is_active` | VARCHAR(5) | TRUE/FALSE |
| `max_employees` | INTEGER | Subscription license limit |
| `subscription_plan` | VARCHAR(20) | starter / business / enterprise |
| `created_at` | TIMESTAMP | Account creation timestamp (+07:00) |

### Relationships
- Parent to: `departments`, `employees`, `assets`, `software_catalog`, `licenses`
- All other datasets filter by `company_id`

---

## 2. departments.csv

| Column | Type | Description |
|--------|------|-------------|
| `department_id` | VARCHAR(10) | Primary key. Format: `dept-NN` |
| `company_id` | VARCHAR(10) | FK → companies.company_id |
| `name` | VARCHAR(50) | Department full name |
| `code` | VARCHAR(10) | Short code (IT, FIN, HR, MKT, etc.) |
| `cost_center` | VARCHAR(20) | Financial cost center code |
| `is_active` | VARCHAR(5) | TRUE/FALSE |

### Departments Included

| Code | Name |
|------|------|
| IT | Information Technology |
| FIN | Finance & Accounting |
| HR | Human Resources |
| MKT | Marketing |
| SALES | Sales |
| LEGAL | Legal & Compliance |
| OPS | Operations |
| PROC | Procurement |
| SUPPORT | Customer Support |
| EXEC | Executive Management |

### Relationships
- Parent to: `employees`

---

## 3. employees.csv

| Column | Type | Description |
|--------|------|-------------|
| `employee_id` | VARCHAR(10) | Primary key. Format: `emp-NNN` |
| `company_id` | VARCHAR(10) | FK → companies.company_id |
| `department_id` | VARCHAR(10) | FK → departments.department_id |
| `full_name` | VARCHAR(100) | Indonesian full name (first + last) |
| `first_name` | VARCHAR(50) | Given name |
| `last_name` | VARCHAR(50) | Family name (Indonesian, Chinese-Indonesian, Batak, Javanese) |
| `email` | VARCHAR(100) | Company email |
| `phone` | VARCHAR(30) | Mobile phone (+62 format) |
| `position` | VARCHAR(100) | Job title |
| `department_name` | VARCHAR(50) | Denormalized department name |
| `employment_status` | VARCHAR(20) | active / notice / offboarding / inactive |
| `join_date` | DATE | Hire date (2019–2025 range) |
| `resign_date` | DATE | Resignation date (inactive only) |
| `manager_id` | VARCHAR(10) | FK → employees.employee_id (self-referencing) |

### Distribution
- **IT:** 20 employees
- **Finance:** 12 employees
- **Operations:** 12 employees
- **Marketing / Sales / Support:** 10 each
- **HR:** 8 employees
- **Executive:** 7 employees
- **Procurement:** 6 employees
- **Legal:** 5 employees

### Status Breakdown
- ~80% active, ~5% notice, ~5% offboarding, ~5% inactive

### Relationships
- Parent to: `assets` (via current_employee_id), `software_usage_logs`
- Referenced by: `qr_codes` (via printed_by/scanned_by)

---

## 4. asset_categories.csv

| Column | Type | Description |
|--------|------|-------------|
| `category_id` | VARCHAR(10) | Primary key. Format: `cat-NN` |
| `company_id` | VARCHAR(10) | FK → companies.company_id |
| `name` | VARCHAR(50) | Category display name |
| `code` | VARCHAR(20) | Short code |
| `is_depreciable` | VARCHAR(5) | TRUE/FALSE |
| `useful_life_months` | INTEGER | Depreciation period (empty for non-depreciable) |

### Categories

| ID | Name | Depreciable | Life (months) |
|----|------|-------------|---------------|
| cat-01 | Laptop | Yes | 36 |
| cat-02 | Desktop | Yes | 48 |
| cat-03 | Monitor | Yes | 60 |
| cat-04 | Smartphone | Yes | 24 |
| cat-05 | Printer | Yes | 60 |
| cat-06 | Server | Yes | 60 |
| cat-07 | Network Switch | Yes | 84 |
| cat-08 | Router | Yes | 60 |
| cat-09 | Tablet | Yes | 36 |
| cat-10 | Peripheral | No | — |

### Relationships
- Parent to: `assets`

---

## 5. assets.csv

| Column | Type | Description |
|--------|------|-------------|
| `asset_id` | VARCHAR(12) | Primary key. Format: `ast-NNNNN` |
| `company_id` | VARCHAR(10) | FK → companies.company_id |
| `category_id` | VARCHAR(10) | FK → asset_categories.category_id |
| `category_name` | VARCHAR(50) | Denormalized category name |
| `asset_tag` | VARCHAR(15) | Human-readable tag: `AST-NNNNN` |
| `brand` | VARCHAR(50) | Manufacturer brand |
| `model` | VARCHAR(100) | Product model name |
| `serial_number` | VARCHAR(50) | Manufacturer serial (unique) |
| `purchase_date` | DATE | Date of purchase (2020–2025) |
| `purchase_price` | NUMERIC(10,2) | Purchase cost in USD |
| `warranty_expiry` | DATE | Warranty end date |
| `status` | VARCHAR(20) | available / assigned / maintenance / retired / lost / stolen |
| `condition` | VARCHAR(20) | new / good / fair / poor / damaged / repairing |
| `current_employee_id` | VARCHAR(10) | FK → employees.employee_id (assigned assets only) |
| `location` | VARCHAR(50) | Physical or logical location |
| `notes` | TEXT | Free-text notes |

### Asset Distribution

| Category | Count | Approx. % |
|----------|-------|-----------|
| Laptop | ~150 | 30% |
| Monitor | ~75 | 15% |
| Smartphone | ~60 | 12% |
| Peripheral | ~50 | 10% |
| Desktop | ~40 | 8% |
| Tablet | ~35 | 7% |
| Server | ~25 | 5% |
| Network Switch | ~25 | 5% |
| Router | ~25 | 5% |
| Printer | ~15 | 3% |

### Status Distribution
- ~35% available, ~45% assigned, ~10% maintenance, ~7% retired, ~2% lost, ~1% stolen

### Brands Included
Dell, HP, Lenovo, Apple, Microsoft, ASUS, LG, Samsung, Google, Xiaomi, Brother, Epson, Canon, Cisco, Ubiquiti, MikroTik, Juniper, Fortinet, Logitech, Jabra, Poly, Supermicro

### Relationships
- Parent to: `qr_codes` (one-to-one)
- Referenced by: `software_usage_logs` (indirect via employee)

---

## 6. qr_codes.csv

| Column | Type | Description |
|--------|------|-------------|
| `qr_id` | VARCHAR(10) | Primary key. Format: `qr-NNNNN` |
| `asset_id` | VARCHAR(12) | FK → assets.asset_id (UNIQUE) |
| `asset_tag` | VARCHAR(15) | Denormalized asset tag |
| `qr_value` | VARCHAR(24) | Globally unique SHA-256 hash (hex, uppercase) |
| `is_printed` | VARCHAR(5) | Whether physical QR label has been printed |
| `scan_count` | INTEGER | Number of times scanned via Field App |

### Business Rules
- One QR code per asset (one-to-one)
- QR values are globally unique (supports cross-tenant scanning)
- Scan count tracks physical inventory verification frequency

---

## 7. software_catalog.csv

| Column | Type | Description |
|--------|------|-------------|
| `software_id` | VARCHAR(10) | Primary key. Format: `sw-NN` |
| `company_id` | VARCHAR(10) | FK → companies.company_id |
| `name` | VARCHAR(100) | Software product name |
| `vendor` | VARCHAR(100) | Publisher/vendor name |
| `license_model` | VARCHAR(20) | per_seat / per_user / per_host / enterprise |
| `is_cloud` | VARCHAR(5) | TRUE (SaaS) / FALSE (on-premise) |
| `monthly_cost_per_seat` | NUMERIC(8,2) | Monthly cost per user in USD |
| `annual_cost_per_seat` | NUMERIC(8,2) | Annual cost per user in USD |
| `category` | VARCHAR(30) | Functional category |

### Software List

| # | Software | Vendor | Model | Cloud | Monthly |
|---|----------|--------|-------|-------|---------|
| 1 | Microsoft 365 Business Premium | Microsoft | per_seat | Yes | $22.00 |
| 2 | Adobe Creative Cloud All Apps | Adobe | per_seat | Yes | $54.99 |
| 3 | Slack Enterprise Grid | Slack | per_user | Yes | $15.00 |
| 4 | Zoom Business | Zoom Video | per_user | Yes | $19.99 |
| 5 | Notion Team Plan | Notion Labs | per_user | Yes | $10.00 |
| 6 | GitHub Enterprise | GitHub/Microsoft | per_user | Yes | $21.00 |
| 7 | Jira Software Cloud | Atlassian | per_user | Yes | $7.75 |
| 8 | Confluence Cloud | Atlassian | per_user | Yes | $6.00 |
| 9 | AutoCAD LT | Autodesk | per_seat | No | $50.00 |
| 10 | Figma Professional | Figma | per_seat | Yes | $12.00 |
| 11 | Salesforce Sales Cloud | Salesforce | per_user | Yes | $75.00 |
| 12 | HubSpot Enterprise | HubSpot | per_user | Yes | $50.00 |
| 13 | Atlassian Bitbucket | Atlassian | per_user | Yes | $6.00 |
| 14 | Datadog Infrastructure | Datadog | per_host | Yes | $15.00 |
| 15 | AWS Business Support | AWS | enterprise | Yes | $100.00 |
| 16 | Tableau Creator | Salesforce/Tableau | per_user | Yes | $70.00 |
| 17 | Power BI Pro | Microsoft | per_user | Yes | $10.00 |
| 18 | Monday.com Enterprise | Monday.com | per_user | Yes | $22.00 |
| 19 | Zendesk Suite | Zendesk | per_user | Yes | $55.00 |
| 20 | DocuSign Enterprise | DocuSign | per_user | Yes | $40.00 |

### Relationships
- Parent to: `licenses`, `software_usage_logs`

---

## 8. licenses.csv

| Column | Type | Description |
|--------|------|-------------|
| `license_id` | VARCHAR(10) | Primary key. Format: `lic-NN` |
| `company_id` | VARCHAR(10) | FK → companies.company_id |
| `software_id` | VARCHAR(10) | FK → software_catalog.software_id |
| `software_name` | VARCHAR(100) | Denormalized software name |
| `license_type` | VARCHAR(20) | subscription / perpetual |
| `total_licenses` | INTEGER | Total seats purchased |
| `used_licenses` | INTEGER | Seats currently assigned |
| `available_licenses` | INTEGER | Unused seats (total - used) |
| `renewal_date` | DATE | Next renewal date (2026) |
| `monthly_cost` | NUMERIC(8,2) | Cost per seat per month |
| `annual_cost` | NUMERIC(8,2) | Cost per seat per year |
| `total_monthly_cost` | NUMERIC(10,2) | Monthly cost × total seats |
| `total_annual_cost` | NUMERIC(10,2) | Annual cost × total seats |
| `status` | VARCHAR(10) | active / expired |

### Key Metrics (all software combined)
- Total licenses: ~700–900 seats
- Utilization rate: varies by software
- Annual SaaS spend: ~$50K–$80K

### Relationships
- Referenced by: `software_usage_logs`

---

## 9. software_usage_logs.csv (20,000 rows)

**This is the most important dataset for AI/ML training.**

| Column | Type | Description |
|--------|------|-------------|
| `log_id` | INTEGER | Sequential primary key |
| `employee_id` | VARCHAR(10) | FK → employees.employee_id |
| `employee_name` | VARCHAR(100) | Denormalized employee name |
| `employee_email` | VARCHAR(100) | Denormalized employee email |
| `department` | VARCHAR(50) | Denormalized department name |
| `software_id` | VARCHAR(10) | FK → software_catalog.software_id |
| `software_name` | VARCHAR(100) | Denormalized software name |
| `login_date` | DATE | Calendar date of login |
| `login_time` | TIME (HH:MM:SS) | Login timestamp (07:00–18:00 WIB) |
| `logout_time` | TIME (HH:MM:SS) | Logout timestamp |
| `session_duration_minutes` | INTEGER | Session length (15–480 min) |
| `device` | VARCHAR(30) | Device type used |
| `ip_address` | VARCHAR(15) | Internal IP (10.x.x.x) |
| `operating_system` | VARCHAR(30) | OS of the device |
| `country` | VARCHAR(20) | Access country |
| `login_status` | VARCHAR(10) | Success / Failed |

### Usage Patterns (Designed for ML Training)

| Pattern | % of Assignments | Behavior |
|---------|-----------------|----------|
| **Dormant** | ~12% | Assigned license but **ZERO** login records — never activated |
| **Very Light** | ~15% | Log in 1–2 days per month |
| **Light** | ~25% | Log in 4–8 days per month (~1–2 days/week) |
| **Regular** | ~33% | Log in 12–20 days per month (~3–4 days/week) |
| **Heavy** | ~15% | Log in 22–28 days per month (daily) |

### AI/ML Use Cases
- **Isolation Forest:** Dormant account detection (employees with zero usage)
- **Time-Series Forecasting:** Monthly active user counts per software
- **Anomaly Detection:** Unusual session durations, off-hours logins
- **Usage Analytics:** Department-level adoption rates

### Time Period
- **Date range:** 2025-07-01 to 2026-06-30 (12 months)
- Granularity: daily login sessions

### Device Distribution
Windows Laptop, MacBook Pro, Windows Desktop, iPhone, Android Phone, iPad, Linux Workstation

---

## 10. prediction_history.csv

| Column | Type | Description |
|--------|------|-------------|
| `prediction_id` | VARCHAR(20) | Primary key |
| `company_id` | VARCHAR(10) | FK → companies.company_id |
| `software_id` | VARCHAR(10) | FK → software_catalog.software_id |
| `software_name` | VARCHAR(100) | Denormalized software name |
| `prediction_type` | VARCHAR(20) | license_forecast / dormant_detection |
| `model_name` | VARCHAR(30) | ML model identifier |
| `model_version` | VARCHAR(10) | Model version |
| `prediction_date` | DATE | Prediction target date |
| `predicted_license_demand` | INTEGER | Forecasted seat count |
| `actual_license_demand` | INTEGER | Actual observed count |
| `confidence_score` | NUMERIC(5,4) | Model confidence (0.75–0.99) |
| `is_anomaly` | VARCHAR(5) | TRUE for anomaly detection results |

### Prediction Types
- **license_forecast (120 rows):** 6 monthly forecasts per software (Prophet model)
- **dormant_detection (15 rows):** Isolation Forest anomaly results for 5 flagged software products

### ML Models Referenced
- `Prophet-v2` (v2.3.1) — Time-series forecasting
- `IsolationForest-v1` (v1.0.2) — Anomaly detection

---

## 11. recommendations.csv

| Column | Type | Description |
|--------|------|-------------|
| `recommendation_id` | VARCHAR(30) | Primary key |
| `company_id` | VARCHAR(10) | FK → companies.company_id |
| `prediction_id` | VARCHAR(20) | FK → prediction_history.prediction_id |
| `software_name` | VARCHAR(100) | Denormalized software name |
| `recommendation_type` | VARCHAR(20) | license_reduce / revoke_dormant / cost_saving |
| `title` | VARCHAR(200) | Short recommendation summary |
| `description` | TEXT | Detailed explanation with savings estimate |
| `priority` | VARCHAR(10) | low / medium / high |
| `estimated_monthly_savings` | NUMERIC(10,2) | Projected cost savings in USD |
| `status` | VARCHAR(15) | pending / applied / dismissed |
| `created_at` | TIMESTAMP | Generation timestamp |

### Business Impact
- Total estimated savings from all recommendations: varies
- High-priority recommendations: dormant account revocations
- Medium-priority: license reductions based on forecast

---

## 12. ai_chat_history.csv

| Column | Type | Description |
|--------|------|-------------|
| `chat_id` | VARCHAR(20) | Primary key |
| `company_id` | VARCHAR(10) | FK → companies.company_id |
| `user_id` | VARCHAR(10) | FK → employees.employee_id |
| `user_name` | VARCHAR(100) | Denormalized user name |
| `session_id` | VARCHAR(15) | Groups messages into conversations |
| `role` | VARCHAR(10) | user / assistant |
| `message` | TEXT | Message content |
| `tokens_used` | INTEGER | LLM token count |
| `model_used` | VARCHAR(20) | Model identifier (assistant only) |
| `retrieved_documents` | INTEGER | Number of RAG documents retrieved |
| `feedback_score` | INTEGER | User rating (1–5, nullable) |
| `created_at` | TIMESTAMP | Message timestamp (+07:00) |

### Usage Patterns
- 30 users with 2–6 messages per conversation
- Topics: offboarding procedure, password reset, asset policies, license costs, security policy
- Feedback collected on ~50% of assistant responses (avg score: 3–5)

### RAG Knowledge Sources
Questions reference: IT SOP, HR SOP, Company Policies, Asset Manuals, Software Documentation, Security Guidelines, Offboarding Checklist, FAQ

---

## 13. audit_logs.csv

| Column | Type | Description |
|--------|------|-------------|
| `audit_id` | INTEGER | Sequential primary key |
| `company_id` | VARCHAR(10) | FK → companies.company_id |
| `user_id` | VARCHAR(10) | FK → employees.employee_id |
| `action` | VARCHAR(30) | Action performed |
| `entity_type` | VARCHAR(20) | Affected entity type |
| `entity_id` | VARCHAR(15) | Affected record reference |
| `ip_address` | VARCHAR(15) | Client IP address |
| `user_agent` | TEXT | Client user agent string |
| `created_at` | TIMESTAMP | Event timestamp (+07:00) |

### Action Types
user.login, user.logout, asset.create, asset.update, asset.assign, asset.return, license.assign, license.revoke, employee.create, employee.update, employee.offboard, software.create, license.create, settings.update, report.generate, ai.query, ai.prediction.run

### Client Types
- Web: Chrome 120, Safari 605, Firefox 121
- Mobile: Flutter (iOS 17.2, Android 14)

---

## 14. notifications.csv

| Column | Type | Description |
|--------|------|-------------|
| `notification_id` | VARCHAR(12) | Primary key |
| `company_id` | VARCHAR(10) | FK → companies.company_id |
| `user_id` | VARCHAR(10) | FK → employees.employee_id (recipient) |
| `type` | VARCHAR(20) | Notification category |
| `severity` | VARCHAR(10) | info / warning / critical |
| `title` | VARCHAR(100) | Short alert title |
| `message` | VARCHAR(200) | Alert body text |
| `is_read` | VARCHAR(5) | TRUE/FALSE |
| `reference_type` | VARCHAR(20) | Related entity type |
| `reference_id` | VARCHAR(15) | Related entity reference |
| `created_at` | TIMESTAMP | Generation timestamp |

### Notification Types
- **license_expiry:** Software licenses expiring within 30 days
- **dormant_account:** Inactive software accounts detected
- **asset_overdue:** Overdue asset returns
- **offboarding:** Employee offboarding in progress
- **maintenance_due:** Scheduled asset maintenance
- **prediction:** New AI forecast available
- **recommendation:** Cost-saving opportunity identified

---

## AI & ML Data Usage

### RAG (Enterprise AI Assistant)

| Dataset | Role |
|---------|------|
| `ai_chat_history.csv` | Training/fine-tuning data. Query patterns, feedback scores, retrieved document references |
| — | External knowledge documents (IT SOP, HR SOP, company policies) are referenced but stored externally in a vector database |

### Time-Series Forecasting (Prophet)

| Dataset | Features |
|---------|----------|
| `software_usage_logs.csv` | Daily active user counts per software, session durations, login frequency (7/30/90-day rolling) |
| `licenses.csv` | Quantity purchased, used, utilization rate |
| — | Headcount from `employees.csv` as demand driver |

### Isolation Forest (Anomaly Detection)

| Dataset | Features |
|---------|----------|
| `software_usage_logs.csv` | Days since last activity per employee-software pair, 30-day active day count, session count trend |
| — | Employment status, department from `employees.csv` for organizational context |

### Dashboard Analytics

| Dataset | Metrics |
|---------|---------|
| `assets.csv` | Total assets, status distribution, category distribution, condition breakdown |
| `employees.csv` | Active headcount, department distribution |
| `licenses.csv` | Utilization rate (used/purchased), upcoming expirations |
| `software_usage_logs.csv` | Active vs dormant users per software, usage trends |
| `notifications.csv` | Unread alert counts by severity |
| `predictions.csv` | Forecast vs actual comparison, confidence trends |
| `recommendations.csv` | Applied savings, pending actions, priority distribution |
| `audit_logs.csv` | Activity volume by action type, user activity timeline |

---

## Foreign Key Relationships Summary

```
companies (comp-001)
├── departments (dept-01–10)
├── employees (emp-001–100)
│   ├── assets (ast-00001–500) via current_employee_id
│   └── software_usage_logs (log 1–20000) via employee_id
├── assets (ast-00001–500)
│   └── qr_codes (qr-00001–500) one-to-one
├── asset_categories (cat-01–10)
├── software_catalog (sw-01–20)
│   └── licenses (lic-01–20)
│       └── software_usage_logs (log 1–20000) via software_id
├── prediction_history (pred-*)
│   └── recommendations (reco-*)
├── ai_chat_history (chat-*)
├── audit_logs (audit 1–300)
└── notifications (notif-001–100)
```

---

## Data Quality Notes

1. **UUID consistency:** Foreign key references across files use matching ID formats — any `emp-NNN` in `assets.csv` exists in `employees.csv`.
2. **Dormant accounts:** ~12% of employee-software assignments have zero usage logs (designed for Isolation Forest training).
3. **Realistic timestamps:** Login times are within working hours (07:00–18:00 WIB), session durations are plausible (15 min to 8 hours).
4. **Indonesian context:** Employee names, addresses, phone numbers, and timezones (+07:00 WIB) reflect an Indonesian enterprise.
5. **No PII:** All data is synthetically generated. No real person data is included.
