const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const OUTPUT_DIR = "D:\\SB4_University\\Artificial Intelligence\\UAS_Nayla\\AssetOptima\\datasets\\raw";

function uuidFromInt(n) {
  const hash = crypto.createHash("md5").update(String(n)).digest("hex");
  return `${hash.slice(0,8)}-${hash.slice(8,12)}-${hash.slice(12,16)}-${hash.slice(16,20)}-${hash.slice(20,32)}`;
}

function randomDate(start, end) {
  const s = new Date(start);
  const e = new Date(end);
  return new Date(s.getTime() + Math.random() * (e.getTime() - s.getTime()));
}

function randomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function pick(arr) {
  if (!arr || arr.length === 0) return "";
  return arr[randomInt(0, arr.length - 1)];
}

function pickWeighted(items, weights) {
  const total = weights.reduce((a, b) => a + b, 0);
  let r = Math.random() * total;
  for (let i = 0; i < items.length; i++) {
    r -= weights[i];
    if (r <= 0) return items[i];
  }
  return items[items.length - 1];
}

function formatDate(d) {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

function writeCSV(filename, rows) {
  if (!rows || rows.length === 0) {
    console.log(`  ! ${filename} (0 rows, skipping)`);
    return;
  }
  const headers = Object.keys(rows[0]);
  const lines = [headers.join(",")];
  for (const row of rows) {
    const vals = headers.map(h => {
      const v = row[h];
      if (v === null || v === undefined) return "";
      const s = String(v);
      if (s.includes(",") || s.includes('"') || s.includes("\n")) {
        return `"${s.replace(/"/g, '""')}"`;
      }
      return s;
    });
    lines.push(vals.join(","));
  }
  fs.writeFileSync(path.join(OUTPUT_DIR, filename), "\ufeff" + lines.join("\n"), "utf-8");
  console.log(`  ✓ ${filename} (${rows.length} rows)`);
}

// ══════════════════════════════════════════════════════════════════════════════
// CONSTANTS
// ══════════════════════════════════════════════════════════════════════════════

const COMPANIES = [
  ["PT Global Solusi Teknologi", "GST", "Enterprise IT Solutions"],
  ["PT Bank Digital Nusantara", "BDN", "Digital Banking"],
  ["PT Ecommerce Maju Bersama", "EMB", "E-commerce Platform"],
  ["PT Rumah Sakit Sejahtera", "RSS", "Healthcare Provider"],
  ["PT Universitas Harapan Bangsa", "UHB", "Education Institution"],
  ["PT Manufaktur Indonesia Jaya", "MIJ", "Manufacturing"],
  ["PT Asuransi Jiwa Kita", "AJK", "Insurance"],
  ["PT Logistik Express Nusantara", "LEN", "Logistics & Supply Chain"],
  ["PT Media Digital Kreatif", "MDK", "Media & Entertainment"],
  ["PT Energi Terbarukan Mandiri", "ETM", "Renewable Energy"],
];

const DEPARTMENTS_DATA = [
  ["Information Technology", "IT"],
  ["Finance & Accounting", "FIN"],
  ["Human Resources", "HR"],
  ["Marketing", "MKT"],
  ["Sales", "SALES"],
  ["Legal & Compliance", "LEGAL"],
  ["Operations", "OPS"],
  ["Procurement", "PROC"],
  ["Customer Support", "SUPPORT"],
  ["Executive Management", "EXEC"],
];

const FIRST_NAMES_MALE = [
  "Agus","Bambang","Cahyo","Dede","Eko","Fajar","Gunawan","Hendra",
  "Indra","Joko","Kadek","Lutfi","Mulyono","Nugroho","Oka","Putu",
  "Rudi","Slamet","Teguh","Ujang","Wahyu","Yusuf","Zainal","Adi",
  "Bayu","Candra","Dimas","Edi","Fitrianto","Gilang","Heru","Irfan",
  "Jatmiko","Kurniawan","Lukman","Mahmud","Nanda","Pramono","Rahmat","Surya"
];

const FIRST_NAMES_FEMALE = [
  "Ani","Bunga","Citra","Dewi","Endah","Fitri","Gita","Hesti",
  "Indah","Juwita","Kartika","Lestari","Mega","Nia","Olivia",
  "Puspita","Ratna","Sari","Tina","Utami","Vina","Wulan","Yuli",
  "Zahra","Ayu","Bella","Cynthia","Dian","Elok","Farah","Gadis",
  "Hana","Ika","Jenny","Kiki","Laras","Nurul","Putri","Rina","Silvi"
];

const LAST_NAMES = [
  "Santoso","Wijaya","Kusuma","Pratama","Wibowo","Hartono","Siregar",
  "Nasution","Saragih","Simanjuntak","Saputra","Gunawan","Susanto",
  "Hidayat","Nugroho","Halim","Lie","Tan","Lim","Ong","Salim",
  "Tjahyadi","Sugiharto","Purnomo","Setiawan","Hermawan","Atmaja",
  "Dwiyanto","Winarso","Mulyadi","Suharto","Irawan","Handoko",
  "Supriyadi","Sudrajat","Haryanto","Maryono","Susilo","Prasetyo","Yulianto"
];

const POSITIONS_BY_DEPT = {
  "IT": ["IT Manager","System Administrator","Network Engineer","Security Analyst","Database Administrator","Helpdesk Support","DevOps Engineer","IT Director","Cloud Architect","IT Support Specialist"],
  "FIN": ["Finance Manager","Accountant","Financial Analyst","Tax Specialist","Treasury Analyst","Internal Auditor","CFO","Payroll Specialist","Accounts Payable","Accounts Receivable"],
  "HR": ["HR Manager","HR Generalist","Recruitment Specialist","Training Coordinator","Compensation Analyst","HRIS Analyst","HR Director","Employee Relations Specialist","Benefits Administrator","HR Assistant"],
  "MKT": ["Marketing Manager","Digital Marketing Specialist","Content Writer","SEO Specialist","Social Media Manager","Brand Strategist","CMO","Marketing Analyst","Graphic Designer","Campaign Coordinator"],
  "SALES": ["Sales Manager","Account Executive","Sales Representative","Business Development","Key Account Manager","Sales Analyst","VP of Sales","Inside Sales Specialist","Sales Coordinator","Regional Sales Manager"],
  "LEGAL": ["Legal Counsel","Compliance Officer","Contract Specialist","Legal Assistant","General Counsel","Risk Analyst","Regulatory Affairs Specialist","Corporate Secretary","Paralegal","Policy Analyst"],
  "OPS": ["Operations Manager","Supply Chain Analyst","Logistics Coordinator","Quality Assurance Specialist","Process Improvement Lead","COO","Facility Manager","Operations Analyst","Project Manager","Vendor Coordinator"],
  "PROC": ["Procurement Manager","Purchasing Specialist","Vendor Manager","Sourcing Analyst","Contract Administrator","Procurement Director","Strategic Sourcing Lead","Buyer","Category Manager","Supply Chain Planner"],
  "SUPPORT": ["Customer Service Manager","Support Agent","Technical Support","Customer Success Manager","Support Analyst","Call Center Lead","Client Relations Specialist","Support Engineer","Escalation Specialist","Quality Monitoring Analyst"],
  "EXEC": ["CEO","CTO","CIO","COO","CFO","CMO","VP of Engineering","VP of Operations","Board Secretary","Executive Assistant"],
};

const SOFTWARE_CATALOG = [
  ["Microsoft 365 Business Premium","Microsoft","per_seat",true,22.00,264.00],
  ["Adobe Creative Cloud All Apps","Adobe","per_seat",true,54.99,659.88],
  ["Slack Enterprise Grid","Slack","per_user",true,15.00,180.00],
  ["Zoom Business","Zoom Video Communications","per_user",true,19.99,239.88],
  ["Notion Team Plan","Notion Labs","per_user",true,10.00,120.00],
  ["GitHub Enterprise","GitHub/Microsoft","per_user",true,21.00,252.00],
  ["Jira Software Cloud","Atlassian","per_user",true,7.75,93.00],
  ["Confluence Cloud","Atlassian","per_user",true,6.00,72.00],
  ["AutoCAD LT","Autodesk","per_seat",false,50.00,600.00],
  ["Figma Professional","Figma","per_seat",true,12.00,144.00],
  ["Salesforce Sales Cloud","Salesforce","per_user",true,75.00,900.00],
  ["HubSpot Enterprise","HubSpot","per_user",true,50.00,600.00],
  ["Atlassian Bitbucket","Atlassian","per_user",true,6.00,72.00],
  ["Datadog Infrastructure","Datadog","per_host",true,15.00,180.00],
  ["AWS Business Support","Amazon Web Services","enterprise",true,100.00,1200.00],
  ["Tableau Creator","Salesforce/Tableau","per_user",true,70.00,840.00],
  ["Power BI Pro","Microsoft","per_user",true,10.00,120.00],
  ["Monday.com Enterprise","Monday.com","per_user",true,22.00,264.00],
  ["Zendesk Suite","Zendesk","per_user",true,55.00,660.00],
  ["DocuSign Enterprise","DocuSign","per_user",true,40.00,480.00],
];

const ASSET_CATEGORIES_DATA = [
  ["Laptop",true,36],["Desktop",true,48],["Monitor",true,60],["Smartphone",true,24],
  ["Printer",true,60],["Server",true,60],["Network Switch",true,84],["Router",true,60],
  ["Tablet",true,36],["Peripheral",false,null],
];

const CATEGORY_ASSETS = {
  "Laptop": [["Dell","Latitude 5540"],["Dell","XPS 15 9530"],["HP","EliteBook 840 G10"],["HP","ProBook 450 G10"],["Lenovo","ThinkPad X1 Carbon Gen 11"],["Lenovo","ThinkPad T14s Gen 4"],["Apple","MacBook Pro 14 M3"],["Apple","MacBook Air 15 M3"],["Microsoft","Surface Laptop 5"],["ASUS","ZenBook 14 OLED"]],
  "Desktop": [["Dell","OptiPlex 7000 Tower"],["HP","EliteDesk 800 G9"],["Lenovo","ThinkCentre M90s Gen 4"],["Apple","Mac Mini M2"],["Apple","Mac Studio M2 Max"]],
  "Monitor": [["Dell","U2723QE 4K USB-C Hub"],["Dell","P2423DE 24 16:9"],["HP","E27u G5 27 4K"],["LG","27UP850N 27 4K"],["Samsung","S27A800 27 4K"]],
  "Smartphone": [["Apple","iPhone 15 Pro"],["Apple","iPhone 15"],["Apple","iPhone 14"],["Samsung","Galaxy S24 Ultra"],["Samsung","Galaxy S24"],["Google","Pixel 8 Pro"],["Xiaomi","13T Pro"]],
  "Printer": [["HP","LaserJet Pro M404dn"],["HP","LaserJet Enterprise M507"],["Brother","HL-L2370DW"],["Epson","WorkForce Pro WF-7820"],["Canon","imageRUNNER 2630i"]],
  "Server": [["Dell","PowerEdge R750xs"],["Dell","PowerEdge R650"],["HP","ProLiant DL380 Gen11"],["Lenovo","ThinkSystem SR650 V3"],["Supermicro","SYS-420GP"]],
  "Network Switch": [["Cisco","Catalyst 9200-48P"],["Cisco","Catalyst 9300-48P"],["Ubiquiti","UniFi Switch Pro 48"],["MikroTik","CRS326-24G-2S+RM"],["Juniper","EX3400-48P"]],
  "Router": [["Cisco","ISR 4321"],["Cisco","ISR 1100-8P"],["Ubiquiti","UniFi Dream Machine SE"],["MikroTik","RB4011iGS+RM"],["Fortinet","FortiGate 60F"]],
  "Tablet": [["Apple","iPad Pro 12.9 M2"],["Apple","iPad Air M1"],["Samsung","Galaxy Tab S9 Ultra"],["Samsung","Galaxy Tab S9 FE"],["Microsoft","Surface Pro 9"]],
  "Peripheral": [["Logitech","MX Master 3S Mouse"],["Logitech","MX Keys Keyboard"],["Logitech","C922 Pro Webcam"],["Jabra","Evolve2 65 Headset"],["Poly","Voyager 5200 Headset"]],
};

const CATEGORY_PRICE_RANGES = {
  "Laptop": [1200,3500],"Desktop": [800,3000],"Monitor": [300,1200],"Smartphone": [600,1500],
  "Printer": [200,2000],"Server": [3000,15000],"Network Switch": [500,4000],"Router": [300,2500],
  "Tablet": [400,1200],"Peripheral": [50,300],
};

const STATUSES = ["available","assigned","maintenance","retired","lost","stolen"];
const STATUS_WEIGHTS = [0.35,0.45,0.10,0.07,0.02,0.01];
const CONDITIONS = ["new","good","fair","poor","damaged","repairing"];
const CONDITION_WEIGHTS = [0.15,0.50,0.20,0.10,0.03,0.02];

const DEPT_SOFTWARE_MAP = {
  "IT": [0,2,3,5,6,7,9,13,14,15,16,17],
  "FIN": [0,1,10,11,15,16,18],
  "HR": [0,4,10,11,17,18],
  "MKT": [0,1,3,4,8,9,10,11,17],
  "SALES": [0,2,3,10,11,17,18],
  "LEGAL": [0,18,19],
  "OPS": [0,3,4,6,7,10,14,17,18],
  "PROC": [0,4,10,17,18],
  "SUPPORT": [0,2,3,6,7,10,18],
  "EXEC": [0,2,3,4,10,11,12,13,14],
};

// ══════════════════════════════════════════════════════════════════════════════
// 1. COMPANIES
// ══════════════════════════════════════════════════════════════════════════════

function genCompanies() {
  return COMPANIES.map(([name, code, desc], i) => ({
    company_id: `comp-${String(i+1).padStart(3,"0")}`,
    name, code,
    description: desc,
    tax_id: `${String(randomInt(10,99))}.${String(randomInt(100,999))}.${String(randomInt(100,999))}.${String(randomInt(1,9))}-${String(randomInt(100,999))}.${String(randomInt(10,99))}`,
    phone: `+62-21-${randomInt(1000000,9999999)}`,
    email: `info@${code.toLowerCase()}.co.id`,
    address: `Jl. ${pick(["Sudirman","Thamrin","Kuningan","Gatot Subroto","Rasuna Said"])} No. ${randomInt(1,500)}, Jakarta`,
    is_active: "TRUE",
    max_employees: String(pick([100,250,500,1000,2000])),
    subscription_plan: pick(["starter","business","enterprise"]),
    created_at: `2024-01-${String(randomInt(1,31)).padStart(2,"0")} 09:00:00+07`,
  }));
}

// ══════════════════════════════════════════════════════════════════════════════
// 2. DEPARTMENTS
// ══════════════════════════════════════════════════════════════════════════════

function genDepartments() {
  return DEPARTMENTS_DATA.map(([name, code], i) => ({
    department_id: `dept-${String(i+1).padStart(2,"0")}`,
    company_id: "comp-001",
    name, code,
    cost_center: `CC-${code}-${randomInt(10,99)}`,
    is_active: "TRUE",
  }));
}

// ══════════════════════════════════════════════════════════════════════════════
// 3. EMPLOYEES (100)
// ══════════════════════════════════════════════════════════════════════════════

function genEmployees() {
  const deptCounts = {"dept-01":20,"dept-02":12,"dept-03":8,"dept-04":10,"dept-05":10,"dept-06":5,"dept-07":12,"dept-08":6,"dept-09":10,"dept-10":7};
  const rows = [];
  const usedNames = new Set();
  let empNum = 1;

  for (const [deptId, count] of Object.entries(deptCounts)) {
    const deptIdx = parseInt(deptId.split("-")[1]) - 1;
    const deptCode = DEPARTMENTS_DATA[deptIdx][1];
    const positions = POSITIONS_BY_DEPT[deptCode] || [];

    for (let j = 0; j < count; j++) {
      let isMale = Math.random() > 0.5;
      let first, last, full;
      do {
        first = pick(isMale ? FIRST_NAMES_MALE : FIRST_NAMES_FEMALE);
        last = pick(LAST_NAMES);
        full = `${first} ${last}`;
      } while (usedNames.has(full));
      usedNames.add(full);

      const join = randomDate("2019-01-01", "2025-12-01");
      const status = pickWeighted(
        ["active","active","active","notice","offboarding","inactive"],
        [0.70,0.10,0.05,0.05,0.05,0.05]
      );
      const resign = status === "inactive" ? formatDate(randomDate(join, new Date("2026-03-01"))) : "";

      const email = `${first.toLowerCase()}.${last.toLowerCase()}@company.co.id`;

      rows.push({
        employee_id: `emp-${String(empNum).padStart(3,"0")}`,
        company_id: "comp-001",
        department_id: deptId,
        full_name: full,
        first_name: first,
        last_name: last,
        email,
        phone: `+62-8${randomInt(11,99)}-${randomInt(1000,9999)}-${randomInt(1000,9999)}`,
        position: pick(positions),
        department_name: DEPARTMENTS_DATA[deptIdx][0],
        employment_status: status,
        join_date: formatDate(join),
        resign_date: resign,
      });
      empNum++;
    }
  }

  // Assign managers
  const deptManagers = {};
  for (const r of rows) {
    const d = r.department_id;
    if (!deptManagers[d]) deptManagers[d] = r.employee_id;
    r.manager_id = deptManagers[d];
  }
  const execs = rows.filter(r => r.department_id === "dept-10");
  for (const [d, mgrId] of Object.entries(deptManagers)) {
    if (d === "dept-10") continue;
    for (const r of rows) {
      if (r.employee_id === mgrId && r.department_id !== "dept-10") {
        r.manager_id = execs.length > 0 ? execs[0].employee_id : mgrId;
      }
    }
  }

  return rows;
}

// ══════════════════════════════════════════════════════════════════════════════
// 4. ASSET CATEGORIES
// ══════════════════════════════════════════════════════════════════════════════

function genAssetCategories() {
  return ASSET_CATEGORIES_DATA.map(([name, depr, months], i) => ({
    category_id: `cat-${String(i+1).padStart(2,"0")}`,
    company_id: "comp-001",
    name,
    code: name.toUpperCase().replace(/ /g,"_").substring(0,10),
    is_depreciable: depr ? "TRUE" : "FALSE",
    useful_life_months: months !== null ? String(months) : "",
  }));
}

// ══════════════════════════════════════════════════════════════════════════════
// 5. ASSETS (500)
// ══════════════════════════════════════════════════════════════════════════════

function genAssets(employees) {
  const rows = [];
  const activeEmps = employees.filter(e => e.employment_status === "active");
  const empIds = activeEmps.map(e => e.employee_id);

  const catNames = Object.keys(CATEGORY_ASSETS);
  const catWeights = [0.30,0.08,0.15,0.12,0.03,0.05,0.05,0.05,0.07,0.10];
  const catIdxMap = {};
  ASSET_CATEGORIES_DATA.forEach(([name], i) => { catIdxMap[name] = i; });

  let assignedIdx = 0;

  for (let i = 1; i <= 500; i++) {
    const catName = pickWeighted(catNames, catWeights);
    const catId = `cat-${String(catIdxMap[catName] + 1).padStart(2,"0")}`;
    const [brand, model] = pick(CATEGORY_ASSETS[catName]);
    const [pmin, pmax] = CATEGORY_PRICE_RANGES[catName];
    const price = (Math.random() * (pmax - pmin) + pmin).toFixed(2);

    const status = pickWeighted(STATUSES, STATUS_WEIGHTS);
    const condition = pickWeighted(CONDITIONS, CONDITION_WEIGHTS);

    const purchase = randomDate("2020-01-01", "2025-12-31");
    const warranty = new Date(purchase);
    warranty.setDate(warranty.getDate() + pick([365, 730, 1095, 1460]));

    const serial = `${brand.substring(0,3).toUpperCase()}-${catName.substring(0,4).toUpperCase()}-${randomInt(10000,99999)}-${randomInt(1000,9999)}`;

    let currentEmp = "";
    if (status === "assigned" && assignedIdx < empIds.length) {
      currentEmp = empIds[assignedIdx];
      assignedIdx++;
      if (Math.random() > 0.5) assignedIdx++;
    }

    rows.push({
      asset_id: `ast-${String(i).padStart(5,"0")}`,
      company_id: "comp-001",
      category_id: catId,
      category_name: catName,
      asset_tag: `AST-${String(i).padStart(5,"0")}`,
      brand, model, serial_number: serial,
      purchase_date: formatDate(purchase),
      purchase_price: price,
      warranty_expiry: formatDate(warranty),
      status, condition,
      current_employee_id: currentEmp,
      location: pick(["Jakarta HQ - Floor 1","Jakarta HQ - Floor 2","Jakarta HQ - Floor 3","Jakarta HQ - Floor 4","Jakarta HQ - Floor 5","Warehouse - Jakarta","Warehouse - Bandung","Data Center - Jakarta","Remote - WFH","Branch - Surabaya"]),
      notes: "",
    });
  }
  return rows;
}

// ══════════════════════════════════════════════════════════════════════════════
// 6. QR CODES
// ══════════════════════════════════════════════════════════════════════════════

function genQrCodes(assets) {
  return assets.map(a => ({
    qr_id: `qr-${a.asset_id.split("-")[1]}`,
    asset_id: a.asset_id,
    asset_tag: a.asset_tag,
    qr_value: crypto.createHash("sha256").update(`assetop-${a.asset_tag}-${a.serial_number}`).digest("hex").substring(0,24).toUpperCase(),
    is_printed: Math.random() > 0.15 ? "TRUE" : "FALSE",
    scan_count: String(randomInt(0, 50)),
  }));
}

// ══════════════════════════════════════════════════════════════════════════════
// 7. SOFTWARE CATALOG
// ══════════════════════════════════════════════════════════════════════════════

function genSoftwareCatalog() {
  const cats = ["Productivity","Creative","Communication","Dev Tools","CRM","Analytics","Project Management"];
  return SOFTWARE_CATALOG.map(([name, vendor, model, isCloud, monthly, annual], i) => ({
    software_id: `sw-${String(i+1).padStart(2,"0")}`,
    company_id: "comp-001",
    name, vendor,
    license_model: model,
    is_cloud: isCloud ? "TRUE" : "FALSE",
    monthly_cost_per_seat: monthly.toFixed(2),
    annual_cost_per_seat: annual.toFixed(2),
    category: pick(cats),
  }));
}

// ══════════════════════════════════════════════════════════════════════════════
// 8. LICENSES
// ══════════════════════════════════════════════════════════════════════════════

function genLicenses() {
  return SOFTWARE_CATALOG.map(([name, vendor, model, isCloud, monthly, annual], i) => {
    const total = pick([10,15,20,25,30,40,50,60,75,100]);
    const used = randomInt(1, total);
    const renewal = randomDate("2026-01-01", "2026-12-31");
    return {
      license_id: `lic-${String(i+1).padStart(2,"0")}`,
      company_id: "comp-001",
      software_id: `sw-${String(i+1).padStart(2,"0")}`,
      software_name: name,
      license_type: isCloud ? "subscription" : "perpetual",
      total_licenses: String(total),
      used_licenses: String(used),
      available_licenses: String(total - used),
      renewal_date: formatDate(renewal),
      monthly_cost: monthly.toFixed(2),
      annual_cost: annual.toFixed(2),
      total_monthly_cost: (monthly * total).toFixed(2),
      total_annual_cost: (annual * total).toFixed(2),
      status: "active",
    };
  });
}

// ══════════════════════════════════════════════════════════════════════════════
// 9. SOFTWARE USAGE LOGS (20,000)
// ══════════════════════════════════════════════════════════════════════════════

function genUsageLogs(employees, softwareCatalog) {
  const rows = [];
  const PATTERNS = ["dormant","very_light","light","regular","heavy"];
  const PATTERN_WEIGHTS = [0.12, 0.15, 0.25, 0.33, 0.15];
  const DEVICES = ["Windows Laptop","MacBook Pro","Windows Desktop","iPhone","Android Phone","iPad","Linux Workstation"];
  const OS = ["Windows 11","macOS 14 Sonoma","macOS 15 Sequoia","iOS 17","Android 14","Ubuntu 22.04","Windows 10"];
  const COUNTRIES = ["Indonesia","Indonesia","Indonesia","Singapore","Malaysia","United States","Australia"];
  const IPS = Array.from({length: 20}, () => `10.${randomInt(0,255)}.${randomInt(0,255)}.${randomInt(1,254)}`);
  const LOGIN_STATUSES = ["Success","Success","Success","Success","Failed","Failed"];
  const LOGIN_WEIGHTS = [0.90, 0.03, 0.03, 0.02, 0.01, 0.01];

  const empSoftwareMap = {};
  for (const emp of employees) {
    const dept = emp.department_name;
    const swIndices = DEPT_SOFTWARE_MAP[dept] || [0, 2, 3];
    const nSw = Math.min(randomInt(2, 5), swIndices.length);
    const assigned = [];
    const shuffled = [...swIndices].sort(() => Math.random() - 0.5);
    for (let j = 0; j < nSw; j++) assigned.push(shuffled[j]);
    empSoftwareMap[emp.employee_id] = assigned;
  }

  const startDate = new Date("2025-07-01");
  const endDate = new Date("2026-06-30");
  let rowId = 1;

  for (const emp of employees) {
    const eid = emp.employee_id;
    const swList = empSoftwareMap[eid];
    if (!swList) continue;

    for (const swIdx of swList) {
      const pattern = pickWeighted(PATTERNS, PATTERN_WEIGHTS);
      if (pattern === "dormant") continue; // Zero records

      let daysPerMonth;
      if (pattern === "very_light") daysPerMonth = randomInt(1, 2);
      else if (pattern === "light") daysPerMonth = randomInt(4, 8);
      else if (pattern === "regular") daysPerMonth = randomInt(12, 20);
      else daysPerMonth = randomInt(22, 28);

      const swId = `sw-${String(swIdx+1).padStart(2,"0")}`;
      const swName = SOFTWARE_CATALOG[swIdx][0];

      let current = new Date(startDate);
      while (current <= endDate && rowId <= 20000) {
        const year = current.getFullYear();
        const month = current.getMonth();
        const monthEnd = new Date(year, month + 1, 0);
        const lastDay = Math.min(monthEnd.getDate(), endDate.getDate());
        if (current.getDate() !== 1) {
          current = new Date(year, month, 1);
        }

        const numDays = Math.min(daysPerMonth, lastDay);
        const daySet = new Set();
        while (daySet.size < numDays) {
          daySet.add(randomInt(1, lastDay));
        }
        const days = [...daySet].sort((a,b) => a-b);

        for (const day of days) {
          if (rowId > 20000) break;
          const loginDate = new Date(year, month, day);
          if (loginDate > endDate) break;

          const loginMinOfDay = randomInt(420, 1080); // 07:00 to 18:00 in minutes
          const durMin = randomInt(15, 480);
          let logoutMinOfDay = loginMinOfDay + durMin;
          if (logoutMinOfDay >= 1440) { logoutMinOfDay = 1439; }
          const loginHour = Math.floor(loginMinOfDay / 60);
          const loginMin = loginMinOfDay % 60;
          const logoutHour = Math.floor(logoutMinOfDay / 60);
          const logoutMin = logoutMinOfDay % 60;

          const loginStatus = pickWeighted(LOGIN_STATUSES, LOGIN_WEIGHTS);

          rows.push({
            log_id: String(rowId),
            employee_id: eid,
            employee_name: emp.full_name,
            employee_email: emp.email,
            department: emp.department_name,
            software_id: swId,
            software_name: swName,
            login_date: formatDate(loginDate),
            login_time: `${String(loginHour).padStart(2,"0")}:${String(loginMin).padStart(2,"0")}:00`,
            logout_time: `${String(logoutHour).padStart(2,"0")}:${String(logoutMin).padStart(2,"0")}:00`,
            session_duration_minutes: String(durMin),
            device: pick(DEVICES),
            ip_address: pick(IPS),
            operating_system: pick(OS),
            country: pick(COUNTRIES),
            login_status: loginStatus,
          });
          rowId++;
        }
        current = new Date(year, month + 1, 1);
      }
      if (rowId > 20000) break;
    }
    if (rowId > 20000) break;
  }

  return rows.slice(0, 20000);
}

// ══════════════════════════════════════════════════════════════════════════════
// 10. PREDICTIONS
// ══════════════════════════════════════════════════════════════════════════════

function genPredictions() {
  const rows = [];
  for (let swIdx = 0; swIdx < SOFTWARE_CATALOG.length; swIdx++) {
    const swId = `sw-${String(swIdx+1).padStart(2,"0")}`;
    const swName = SOFTWARE_CATALOG[swIdx][0];
    for (let m = 0; m < 6; m++) {
      const predDate = new Date(2026, 0, 1 + m * 30);
      const base = randomInt(15, 50);
      const predicted = base + randomInt(-3, 3);
      const actual = predicted + randomInt(-5, 5);
      rows.push({
        prediction_id: `pred-${String(swIdx+1).padStart(2,"0")}-${String(m+1).padStart(2,"0")}`,
        company_id: "comp-001",
        software_id: swId,
        software_name: swName,
        prediction_type: "license_forecast",
        model_name: "Prophet-v2",
        model_version: "2.3.1",
        prediction_date: formatDate(predDate),
        predicted_license_demand: String(predicted),
        actual_license_demand: String(actual),
        confidence_score: (Math.random() * 0.23 + 0.75).toFixed(4),
        is_anomaly: "FALSE",
      });
    }
  }

  // Anomaly predictions
  const sampled = [...Array(SOFTWARE_CATALOG.length).keys()].sort(() => Math.random()-0.5).slice(0, 5);
  for (const swIdx of sampled) {
    const swId = `sw-${String(swIdx+1).padStart(2,"0")}`;
    const swName = SOFTWARE_CATALOG[swIdx][0];
    for (let k = 0; k < 3; k++) {
      const predDate = randomDate("2026-01-01", "2026-06-30");
      const dormant = randomInt(2, 12);
      rows.push({
        prediction_id: `pred-anom-${String(swIdx+1).padStart(2,"0")}-${k+1}`,
        company_id: "comp-001",
        software_id: swId,
        software_name: swName,
        prediction_type: "dormant_detection",
        model_name: "IsolationForest-v1",
        model_version: "1.0.2",
        prediction_date: formatDate(predDate),
        predicted_license_demand: String(dormant),
        actual_license_demand: String(dormant + randomInt(-2, 2)),
        confidence_score: (Math.random() * 0.17 + 0.82).toFixed(4),
        is_anomaly: "TRUE",
      });
    }
  }
  return rows;
}

// ══════════════════════════════════════════════════════════════════════════════
// 11. RECOMMENDATIONS
// ══════════════════════════════════════════════════════════════════════════════

function genRecommendations(predictions) {
  const rows = [];
  for (const p of predictions) {
    if (p.prediction_type !== "license_forecast") continue;
    if (Math.random() > 0.4) continue;
    const reduction = randomInt(1, 8);
    const savings = reduction * (Math.random() * 65 + 10);
    rows.push({
      recommendation_id: `reco-${p.prediction_id}`,
      company_id: "comp-001",
      prediction_id: p.prediction_id,
      software_name: p.software_name,
      recommendation_type: pick(["license_reduce","revoke_dormant","cost_saving"]),
      title: `Reduce ${p.software_name} licenses by ${reduction}`,
      description: `AI detected ${reduction} dormant seats in ${p.software_name}. Recommended action: revoke and save estimated $${savings.toFixed(0)}/month.`,
      priority: pick(["low","medium","high"]),
      estimated_monthly_savings: savings.toFixed(2),
      status: pick(["pending","applied","dismissed"]),
      created_at: `${p.prediction_date} 08:00:00+07`,
    });
  }
  // Anomaly recommendations
  for (const p of predictions) {
    if (p.prediction_type !== "dormant_detection") continue;
    const savings = Math.random() * 400 + 100;
    rows.push({
      recommendation_id: `reco-anom-${p.prediction_id}`,
      company_id: "comp-001",
      prediction_id: p.prediction_id,
      software_name: p.software_name,
      recommendation_type: "revoke_dormant",
      title: `Dormant accounts detected in ${p.software_name}`,
      description: `Isolation Forest flagged ${p.predicted_license_demand} dormant users. Estimated annual savings: $${savings.toFixed(0)}.`,
      priority: "high",
      estimated_monthly_savings: savings.toFixed(2),
      status: "pending",
      created_at: `${p.prediction_date} 09:30:00+07`,
    });
  }
  return rows;
}

// ══════════════════════════════════════════════════════════════════════════════
// 12. AI CHAT HISTORY
// ══════════════════════════════════════════════════════════════════════════════

function genChatHistory(employees) {
  const questions = [
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
  ];
  const rows = [];
  const active = employees.filter(e => e.employment_status === "active").slice(0, 30);

  for (let i = 0; i < active.length && rows.length < 250; i++) {
    const u = active[i];
    const sessionId = `sess-${String(i).padStart(4,"0")}`;
    const nMsgs = randomInt(2, 6);
    for (let j = 0; j < nMsgs && rows.length < 250; j++) {
      const q = pick(questions);
      const isUser = j % 2 === 0;
      rows.push({
        chat_id: `chat-${String(i).padStart(4,"0")}-${String(j).padStart(2,"0")}`,
        company_id: "comp-001",
        user_id: u.employee_id,
        user_name: u.full_name,
        session_id: sessionId,
        role: isUser ? "user" : "assistant",
        message: isUser ? q : `Based on the retrieved documents, here is the answer to your question about "${q.split('?')[0]}": [Detailed answer with ${randomInt(3,8)} bullet points covering policies, procedures, and relevant guidelines.]`,
        tokens_used: isUser ? String(randomInt(10, 30)) : String(randomInt(50, 300)),
        model_used: isUser ? "" : "gpt-4o",
        retrieved_documents: isUser ? "" : String(randomInt(1, 5)),
        feedback_score: !isUser && Math.random() > 0.5 ? String(randomInt(3, 5)) : "",
        created_at: `2026-0${randomInt(1,6)}-${String(randomInt(1,28)).padStart(2,"0")} ${String(randomInt(8,17)).padStart(2,"0")}:${String(randomInt(0,59)).padStart(2,"0")}:00+07`,
      });
    }
  }
  return rows;
}

// ══════════════════════════════════════════════════════════════════════════════
// 13. AUDIT LOGS
// ══════════════════════════════════════════════════════════════════════════════

function genAuditLogs(employees) {
  const actions = ["user.login","user.logout","asset.create","asset.update","asset.assign","asset.return","license.assign","license.revoke","employee.create","employee.update","employee.offboard","software.create","license.create","settings.update","report.generate","ai.query","ai.prediction.run"];
  const entities = ["asset","license","employee","software","user","notification"];
  const userAgents = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/605","Flutter/3.16 (Mobile; iOS 17.2)","Flutter/3.16 (Mobile; Android 14)","Mozilla/5.0 (X11; Linux x86_64) Firefox/121"];
  const empIds = employees.filter(e => e.employment_status === "active").map(e => e.employee_id);
  const rows = [];

  for (let i = 1; i <= 300; i++) {
    const action = pick(actions);
    const entity = action.includes("login") || action.includes("logout") ? "user" : pick(entities);
    rows.push({
      audit_id: String(i),
      company_id: "comp-001",
      user_id: pick(empIds),
      action,
      entity_type: entity,
      entity_id: `ref-${String(randomInt(1,500)).padStart(5,"0")}`,
      ip_address: `10.${randomInt(0,255)}.${randomInt(0,255)}.${randomInt(1,254)}`,
      user_agent: pick(userAgents),
      created_at: `2026-0${randomInt(1,6)}-${String(randomInt(1,28)).padStart(2,"0")} ${String(randomInt(0,23)).padStart(2,"0")}:${String(randomInt(0,59)).padStart(2,"0")}:${String(randomInt(0,59)).padStart(2,"0")}+07`,
    });
  }
  return rows;
}

// ══════════════════════════════════════════════════════════════════════════════
// 14. NOTIFICATIONS
// ══════════════════════════════════════════════════════════════════════════════

function genNotifications() {
  const types = [
    ["license_expiry","warning"],["dormant_account","warning"],["asset_overdue","critical"],
    ["offboarding","info"],["maintenance_due","info"],["prediction","info"],["recommendation","info"],
  ];
  const titles = {
    license_expiry: "Software license expiring soon",
    dormant_account: "Dormant software accounts detected",
    asset_overdue: "Asset return is overdue",
    offboarding: "Employee offboarding in progress",
    maintenance_due: "Asset maintenance scheduled",
    prediction: "New AI prediction available",
    recommendation: "Cost-saving recommendation generated",
  };
  const rows = [];
  for (let i = 1; i <= 100; i++) {
    const [nt, sev] = pick(types);
    rows.push({
      notification_id: `notif-${String(i).padStart(3,"0")}`,
      company_id: "comp-001",
      user_id: `emp-${String(randomInt(1,100)).padStart(3,"0")}`,
      type: nt,
      severity: sev,
      title: titles[nt],
      message: `${titles[nt]} — please review and take action.`,
      is_read: Math.random() > 0.5 ? "TRUE" : "FALSE",
      reference_type: pick(["license","asset","employee","prediction"]),
      reference_id: `ref-${String(randomInt(1,500)).padStart(3,"0")}`,
      created_at: `2026-0${randomInt(1,6)}-${String(randomInt(1,28)).padStart(2,"0")} ${String(randomInt(8,17)).padStart(2,"0")}:${String(randomInt(0,59)).padStart(2,"0")}:00+07`,
    });
  }
  return rows;
}

// ══════════════════════════════════════════════════════════════════════════════
// MAIN
// ══════════════════════════════════════════════════════════════════════════════

function main() {
  console.log("Generating AssetOptima Enterprise Datasets...\n");

  if (!fs.existsSync(OUTPUT_DIR)) fs.mkdirSync(OUTPUT_DIR, { recursive: true });

  console.log("[1/14] Companies...");
  const companies = genCompanies();
  writeCSV("companies.csv", companies);

  console.log("[2/14] Departments...");
  const departments = genDepartments();
  writeCSV("departments.csv", departments);

  console.log("[3/14] Employees...");
  const employees = genEmployees();
  writeCSV("employees.csv", employees);

  console.log("[4/14] Asset Categories...");
  const categories = genAssetCategories();
  writeCSV("asset_categories.csv", categories);

  console.log("[5/14] Assets...");
  const assets = genAssets(employees);
  writeCSV("assets.csv", assets);

  console.log("[6/14] QR Codes...");
  const qrCodes = genQrCodes(assets);
  writeCSV("qr_codes.csv", qrCodes);

  console.log("[7/14] Software Catalog...");
  const software = genSoftwareCatalog();
  writeCSV("software_catalog.csv", software);

  console.log("[8/14] Licenses...");
  const licenses = genLicenses();
  writeCSV("licenses.csv", licenses);

  console.log("[9/14] Software Usage Logs (20,000 records - this may take a moment)...");
  const usageLogs = genUsageLogs(employees, software);
  writeCSV("software_usage_logs.csv", usageLogs);
  const usedEmps = new Set(usageLogs.map(r => r.employee_id));
  const dormantCount = 100 - usedEmps.size;
  console.log(`       (Dormant employees with zero logins: ~${dormantCount})`);

  console.log("[10/14] AI Predictions...");
  const predictions = genPredictions();
  writeCSV("prediction_history.csv", predictions);

  console.log("[11/14] AI Recommendations...");
  const recommendations = genRecommendations(predictions);
  writeCSV("recommendations.csv", recommendations);

  console.log("[12/14] AI Chat History...");
  const chat = genChatHistory(employees);
  writeCSV("ai_chat_history.csv", chat);

  console.log("[13/14] Audit Logs...");
  const audit = genAuditLogs(employees);
  writeCSV("audit_logs.csv", audit);

  console.log("[14/14] Notifications...");
  const notifs = genNotifications();
  writeCSV("notifications.csv", notifs);

  console.log(`\nAll datasets generated successfully in:\n   ${OUTPUT_DIR}/`);
}

main();
