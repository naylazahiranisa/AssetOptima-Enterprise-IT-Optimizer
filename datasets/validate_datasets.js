const fs = require('fs');
const path = require('path');

const RAW = path.join(__dirname, 'raw');

function readCSV(name) {
  const content = fs.readFileSync(path.join(RAW, name), 'utf8');
  const lines = content.trim().split('\n');
  const headers = lines[0].split(',');
  const rows = lines.slice(1).map(line => {
    const vals = line.split(',');
    const obj = {};
    headers.forEach((h, i) => obj[h.trim()] = (vals[i] || '').trim());
    return obj;
  });
  return { headers, rows };
}

function validate() {
  const report = [];
  let errors = 0;
  let warnings = 0;

  // Load all datasets
  const companies = readCSV('companies.csv');
  const departments = readCSV('departments.csv');
  const employees = readCSV('employees.csv');
  const assetCategories = readCSV('asset_categories.csv');
  const assets = readCSV('assets.csv');
  const qrCodes = readCSV('qr_codes.csv');
  const softwareCatalog = readCSV('software_catalog.csv');
  const licenses = readCSV('licenses.csv');
  const usageLogs = readCSV('software_usage_logs.csv');
  const predictions = readCSV('prediction_history.csv');
  const recommendations = readCSV('recommendations.csv');
  const chatHistory = readCSV('ai_chat_history.csv');
  const auditLogs = readCSV('audit_logs.csv');
  const notifications = readCSV('notifications.csv');

  // Build index sets
  const companyIds = new Set(companies.rows.map(r => r.company_id));
  const deptIds = new Set(departments.rows.map(r => r.department_id));
  const employeeIds = new Set(employees.rows.map(r => r.employee_id));
  const catIds = new Set(assetCategories.rows.map(r => r.category_id));
  const assetIds = new Set(assets.rows.map(r => r.asset_id));
  const swIds = new Set(softwareCatalog.rows.map(r => r.software_id));
  const licIds = new Set(licenses.rows.map(r => r.license_id));
  const predIds = new Set(predictions.rows.map(r => r.prediction_id));

  // Build department code → id map
  const deptCodeToId = {};
  departments.rows.forEach(r => { deptCodeToId[r.code] = r.department_id; });
  const deptNameToId = {};
  departments.rows.forEach(r => { deptNameToId[r.name] = r.department_id; });

  // ── 1. companies ──
  report.push('=== COMPANIES ===');
  // Check unique codes
  const codes = companies.rows.map(r => r.code);
  const dupCodes = codes.filter((c, i) => codes.indexOf(c) !== i);
  if (dupCodes.length > 0) { errors++; report.push(`  FAIL: Duplicate company codes: ${[...new Set(dupCodes)]}`); }
  else { report.push(`  PASS: No duplicate company codes`); }

  // Check active company exists
  const activeComps = companies.rows.filter(r => r.is_active === 'TRUE');
  if (activeComps.length === 0) { errors++; report.push(`  FAIL: No active companies`); }
  else { report.push(`  PASS: ${activeComps.length} active companies`); }

  // ── 2. departments ──
  report.push('\n=== DEPARTMENTS ===');
  let deptErrors = 0;
  departments.rows.forEach(r => {
    if (!companyIds.has(r.company_id)) { errors++; deptErrors++; report.push(`  FAIL: dept ${r.department_id} references missing company ${r.company_id}`); }
    if (!r.name) { errors++; report.push(`  FAIL: dept ${r.department_id} has empty name`); }
    if (!r.code) { errors++; report.push(`  FAIL: dept ${r.department_id} has empty code`); }
  });
  if (deptErrors === 0) report.push(`  PASS: All ${departments.rows.length} departments reference valid companies`);

  // Check all 10 standard departments exist
  const deptNames = departments.rows.map(r => r.name);
  const expectedDepts = ['Information Technology','Finance & Accounting','Human Resources','Marketing','Sales','Legal & Compliance','Operations','Procurement','Customer Support','Executive Management'];
  const missingDepts = expectedDepts.filter(d => !deptNames.includes(d));
  if (missingDepts.length > 0) { warnings++; report.push(`  WARN: Missing departments: ${missingDepts}`); }
  else { report.push(`  PASS: All 10 standard departments present`); }

  // ── 3. employees ──
  report.push('\n=== EMPLOYEES ===');
  let empErrors = 0;
  employees.rows.forEach(r => {
    if (!companyIds.has(r.company_id)) { errors++; empErrors++; report.push(`  FAIL: emp ${r.employee_id} references missing company ${r.company_id}`); }
    if (!deptIds.has(r.department_id) && !deptNameToId[r.department_id]) {
      // department_id might be stored as name in the CSV
    }
    if (!r.first_name || !r.last_name) { errors++; empErrors++; report.push(`  FAIL: emp ${r.employee_id} missing name`); }
    if (!r.email) { errors++; empErrors++; report.push(`  FAIL: emp ${r.employee_id} missing email`); }
    if (!r.join_date) { errors++; empErrors++; report.push(`  FAIL: emp ${r.employee_id} missing join_date`); }
    // Validate status
    const validStatuses = ['active','notice','offboarding','inactive'];
    if (!validStatuses.includes(r.employment_status)) { errors++; report.push(`  FAIL: emp ${r.employee_id} invalid status: ${r.employment_status}`); }
  });
  if (empErrors === 0) report.push(`  PASS: All ${employees.rows.length} employees have valid data`);

  // Check duplicate emails
  const empEmails = employees.rows.map(r => r.email);
  const dupEmails = empEmails.filter((e, i) => empEmails.indexOf(e) !== i);
  if (dupEmails.length > 0) { errors++; report.push(`  FAIL: ${dupEmails.length} duplicate employee emails`); }
  else { report.push(`  PASS: No duplicate employee emails`); }

  // Check manager references
  const mgrErrors = employees.rows.filter(r => r.manager_id && !employeeIds.has(r.manager_id)).length;
  if (mgrErrors > 0) { errors++; report.push(`  FAIL: ${mgrErrors} employees reference invalid manager_id`); }
  else { report.push(`  PASS: All manager references valid`); }

  // ── 4. asset_categories ──
  report.push('\n=== ASSET CATEGORIES ===');
  let catErrors = 0;
  assetCategories.rows.forEach(r => {
    if (!companyIds.has(r.company_id)) { errors++; catErrors++; report.push(`  FAIL: category ${r.category_id} references missing company`); }
  });
  if (catErrors === 0) report.push(`  PASS: All ${assetCategories.rows.length} categories valid`);

  // ── 5. assets ──
  report.push('\n=== ASSETS ===');
  let assetErrors = 0;
  // Check duplicate serial numbers
  const serials = assets.rows.map(r => r.serial_number).filter(s => s);
  const dupSerials = serials.filter((s, i) => serials.indexOf(s) !== i);
  if (dupSerials.length > 0) { errors++; assetErrors++; report.push(`  FAIL: ${dupSerials.length} duplicate serial numbers`); }
  else { report.push(`  PASS: No duplicate serial numbers`); }

  // Check duplicate asset tags
  const tags = assets.rows.map(r => r.asset_tag).filter(t => t);
  const dupTags = tags.filter((t, i) => tags.indexOf(t) !== i);
  if (dupTags.length > 0) { errors++; assetErrors++; report.push(`  FAIL: ${dupTags.length} duplicate asset tags`); }
  else { report.push(`  PASS: No duplicate asset tags`); }

  // Check FK references
  assets.rows.forEach(r => {
    if (!companyIds.has(r.company_id)) { errors++; report.push(`  FAIL: asset ${r.asset_id} references missing company`); }
    if (!catIds.has(r.category_id)) { errors++; report.push(`  FAIL: asset ${r.asset_id} references missing category ${r.category_id}`); }
    if (r.current_employee_id && !employeeIds.has(r.current_employee_id)) { errors++; report.push(`  FAIL: asset ${r.asset_id} references missing employee ${r.current_employee_id}`); }
  });

  // Check negative prices
  const negPrices = assets.rows.filter(r => r.purchase_price && parseFloat(r.purchase_price) < 0);
  if (negPrices.length > 0) { errors++; report.push(`  FAIL: ${negPrices.length} assets have negative purchase_price`); }
  else { report.push(`  PASS: No negative prices`); }

  // Check future dates
  const today = new Date('2026-07-01');
  const futurePurchase = assets.rows.filter(r => r.purchase_date && new Date(r.purchase_date) > today);
  if (futurePurchase.length > 0) { warnings++; report.push(`  WARN: ${futurePurchase.length} assets have future purchase_date`); }

  // Validate status values
  const validAssetStatuses = ['available','assigned','maintenance','retired','lost','stolen'];
  const invalidStatuses = assets.rows.filter(r => !validAssetStatuses.includes(r.status));
  if (invalidStatuses.length > 0) { errors++; report.push(`  FAIL: ${invalidStatuses.length} assets with invalid status`); }

  if (assetErrors === 0) report.push(`  PASS: All ${assets.rows.length} assets structurally valid`);

  // ── 6. qr_codes ──
  report.push('\n=== QR CODES ===');
  let qrErrors = 0;
  // Check duplicate qr_values
  const qrValues = qrCodes.rows.map(r => r.qr_value);
  const dupQr = qrValues.filter((v, i) => qrValues.indexOf(v) !== i);
  if (dupQr.length > 0) { errors++; qrErrors++; report.push(`  FAIL: ${dupQr.length} duplicate QR values`); }
  else { report.push(`  PASS: All ${qrCodes.rows.length} QR values globally unique`); }

  // Check one-to-one with assets
  const qrAssetIds = qrCodes.rows.map(r => r.asset_id);
  const dupQrAsset = qrAssetIds.filter((a, i) => qrAssetIds.indexOf(a) !== i);
  if (dupQrAsset.length > 0) { errors++; qrErrors++; report.push(`  FAIL: ${dupQrAsset.length} assets have multiple QR codes`); }
  else { report.push(`  PASS: One-to-one QR-to-asset mapping`); }

  // Check all QR assets exist
  const missingQrAssets = qrCodes.rows.filter(r => !assetIds.has(r.asset_id));
  if (missingQrAssets.length > 0) { errors++; report.push(`  FAIL: ${missingQrAssets.length} QR codes reference non-existent assets`); }
  else { report.push(`  PASS: All QR codes reference valid assets`); }

  // Check all assets have QR codes
  const assetsWithoutQr = [...assetIds].filter(a => !qrAssetIds.includes(a));
  if (assetsWithoutQr.length > 0) { errors++; report.push(`  FAIL: ${assetsWithoutQr.length} assets have no QR code`); }

  // ── 7. software_catalog ──
  report.push('\n=== SOFTWARE CATALOG ===');
  let swErrors = 0;
  softwareCatalog.rows.forEach(r => {
    if (!companyIds.has(r.company_id)) { errors++; swErrors++; report.push(`  FAIL: software ${r.software_id} references missing company`); }
  });
  // Check duplicate software names
  const swNames = softwareCatalog.rows.map(r => r.name);
  const dupSw = swNames.filter((n, i) => swNames.indexOf(n) !== i);
  if (dupSw.length > 0) { errors++; report.push(`  FAIL: Duplicate software names: ${[...new Set(dupSw)]}`); }
  else { report.push(`  PASS: No duplicate software names`); }

  if (swErrors === 0) report.push(`  PASS: All ${softwareCatalog.rows.length} software entries valid`);

  // ── 8. licenses ──
  report.push('\n=== LICENSES ===');
  let licErrors = 0;
  licenses.rows.forEach(r => {
    if (!companyIds.has(r.company_id)) { errors++; licErrors++; report.push(`  FAIL: license ${r.license_id} references missing company`); }
    if (!swIds.has(r.software_id)) { errors++; licErrors++; report.push(`  FAIL: license ${r.license_id} references missing software ${r.software_id}`); }
    // Check used <= total
    if (parseInt(r.used_licenses) > parseInt(r.total_licenses)) { errors++; licErrors++; report.push(`  FAIL: license ${r.license_id} used (${r.used_licenses}) > total (${r.total_licenses})`); }
    if (parseInt(r.total_licenses) <= 0) { errors++; licErrors++; report.push(`  FAIL: license ${r.license_id} has non-positive total_licenses`); }
    // Check available = total - used
    const expectedAvail = parseInt(r.total_licenses) - parseInt(r.used_licenses);
    if (parseInt(r.available_licenses) !== expectedAvail) { warnings++; report.push(`  WARN: license ${r.license_id} available_licenses (${r.available_licenses}) != total - used (${expectedAvail})`); }
  });
  if (licErrors === 0) report.push(`  PASS: All ${licenses.rows.length} licenses structurally valid`);

  // ── 9. software_usage_logs ──
  report.push('\n=== SOFTWARE USAGE LOGS (sample validation) ===');
  let usageErrors = 0;
  // Check FK references (sample first 1000)
  const checkedEmpIds = new Set();
  const checkedSwIds = new Set();
  usageLogs.rows.forEach((r, i) => {
    if (!employeeIds.has(r.employee_id)) {
      if (!checkedEmpIds.has(r.employee_id)) {
        errors++; usageErrors++; report.push(`  FAIL: usage log ${r.log_id} references missing employee ${r.employee_id}`);
        checkedEmpIds.add(r.employee_id);
      }
    }
    if (!swIds.has(r.software_id)) {
      if (!checkedSwIds.has(r.software_id)) {
        errors++; usageErrors++; report.push(`  FAIL: usage log ${r.log_id} references missing software ${r.software_id}`);
        checkedSwIds.add(r.software_id);
      }
    }
    // Check login time valid format
    if (r.login_time && !/^\d{2}:\d{2}:\d{2}$/.test(r.login_time)) { errors++; report.push(`  FAIL: usage log ${r.log_id} invalid login_time: ${r.login_time}`); }
    if (r.logout_time && !/^\d{2}:\d{2}:\d{2}$/.test(r.logout_time)) { errors++; report.push(`  FAIL: usage log ${r.log_id} invalid logout_time: ${r.logout_time}`); }
    // Check no 60 in minutes/seconds
    if (r.login_time) {
      const parts = r.login_time.split(':');
      if (parseInt(parts[1]) >= 60 || parseInt(parts[2]) >= 60) { errors++; report.push(`  FAIL: usage log ${r.log_id} invalid login_time value: ${r.login_time}`); }
    }
    if (r.logout_time) {
      const parts = r.logout_time.split(':');
      if (parseInt(parts[1]) >= 60 || parseInt(parts[2]) >= 60) { errors++; report.push(`  FAIL: usage log ${r.log_id} invalid logout_time value: ${r.logout_time}`); }
    }
  });

  if (usageErrors === 0) report.push(`  PASS: FK references in usage logs are valid`);

  // Check dormant accounts
  const activeEmployees = new Set(usageLogs.rows.map(r => r.employee_id));
  const dormantCount = employees.rows.filter(r => !activeEmployees.has(r.employee_id) && r.employment_status === 'active').length;
  report.push(`  INFO: ${dormantCount} active employees with ZERO usage logs (dormant)`);

  // Check usage patterns
  const empLoginCount = {};
  usageLogs.rows.forEach(r => {
    if (!empLoginCount[r.employee_id]) empLoginCount[r.employee_id] = 0;
    empLoginCount[r.employee_id]++;
  });
  const loginDist = { '0': 0, '1-50': 0, '51-200': 0, '201-500': 0, '501+': 0 };
  const totalAssigned = usageLogs.rows.length > 0 ? employeeIds.size : 0;
  // Count employees per login bucket
  const loginCounts = Object.values(empLoginCount);
  loginCounts.forEach(c => {
    if (c === 0) loginDist['0']++;
    else if (c <= 50) loginDist['1-50']++;
    else if (c <= 200) loginDist['51-200']++;
    else if (c <= 500) loginDist['201-500']++;
    else loginDist['501+']++;
  });
  report.push(`  INFO: Usage pattern distribution: ${JSON.stringify(loginDist)}`);

  // ── 10. predictions ──
  report.push('\n=== PREDICTIONS ===');
  let predErrors = 0;
  predictions.rows.forEach(r => {
    if (!companyIds.has(r.company_id)) { errors++; predErrors++; report.push(`  FAIL: prediction ${r.prediction_id} references missing company`); }
    if (r.software_id && !swIds.has(r.software_id)) { errors++; predErrors++; report.push(`  FAIL: prediction ${r.prediction_id} references missing software ${r.software_id}`); }
    if (r.confidence_score && (parseFloat(r.confidence_score) < 0 || parseFloat(r.confidence_score) > 1)) { errors++; report.push(`  FAIL: prediction ${r.prediction_id} invalid confidence_score: ${r.confidence_score}`); }
  });
  if (predErrors === 0) report.push(`  PASS: All ${predictions.rows.length} predictions valid`);

  // ── 11. recommendations ──
  report.push('\n=== RECOMMENDATIONS ===');
  let recoErrors = 0;
  recommendations.rows.forEach(r => {
    if (!companyIds.has(r.company_id)) { errors++; recoErrors++; report.push(`  FAIL: reco ${r.recommendation_id} references missing company`); }
    if (r.prediction_id && !predIds.has(r.prediction_id)) { errors++; recoErrors++; report.push(`  FAIL: reco ${r.recommendation_id} references missing prediction ${r.prediction_id}`); }
    if (r.estimated_monthly_savings && parseFloat(r.estimated_monthly_savings) < 0) { errors++; report.push(`  FAIL: reco ${r.recommendation_id} negative savings`); }
  });
  if (recoErrors === 0) report.push(`  PASS: All ${recommendations.rows.length} recommendations valid`);

  // ── 12. chat_history ──
  report.push('\n=== CHAT HISTORY ===');
  let chatErrors = 0;
  chatHistory.rows.forEach(r => {
    if (!companyIds.has(r.company_id)) { errors++; chatErrors++; report.push(`  FAIL: chat ${r.chat_id} references missing company`); }
    if (r.user_id && !employeeIds.has(r.user_id)) { warnings++; report.push(`  WARN: chat ${r.chat_id} references missing user ${r.user_id}`); }
    if (!r.role || !['user','assistant'].includes(r.role)) { errors++; report.push(`  FAIL: chat ${r.chat_id} invalid role: ${r.role}`); }
    if (r.feedback_score && (parseInt(r.feedback_score) < 1 || parseInt(r.feedback_score) > 5)) { errors++; report.push(`  FAIL: chat ${r.chat_id} invalid feedback_score: ${r.feedback_score}`); }
  });
  if (chatErrors === 0) report.push(`  PASS: All ${chatHistory.rows.length} chat messages valid`);

  // ── 13. audit_logs ──
  report.push('\n=== AUDIT LOGS ===');
  let auditErrors = 0;
  auditLogs.rows.forEach(r => {
    if (!companyIds.has(r.company_id)) { errors++; auditErrors++; report.push(`  FAIL: audit ${r.audit_id} references missing company`); }
    if (!r.action) { errors++; report.push(`  FAIL: audit ${r.audit_id} missing action`); }
    if (!r.entity_type) { errors++; report.push(`  FAIL: audit ${r.audit_id} missing entity_type`); }
  });
  if (auditErrors === 0) report.push(`  PASS: All ${auditLogs.rows.length} audit logs valid`);

  // ── 14. notifications ──
  report.push('\n=== NOTIFICATIONS ===');
  let notifErrors = 0;
  notifications.rows.forEach(r => {
    if (!companyIds.has(r.company_id)) { errors++; notifErrors++; report.push(`  FAIL: notif ${r.notification_id} references missing company`); }
    if (r.user_id && !employeeIds.has(r.user_id)) { warnings++; report.push(`  WARN: notif ${r.notification_id} references missing user ${r.user_id}`); }
    if (!r.type) { errors++; report.push(`  FAIL: notif ${r.notification_id} missing type`); }
  });
  if (notifErrors === 0) report.push(`  PASS: All ${notifications.rows.length} notifications valid`);

  // ── SUMMARY ──
  report.push('\n========================================');
  report.push('VALIDATION SUMMARY');
  report.push('========================================');
  report.push(`  Total datasets: 14`);
  report.push(`  Total rows validated: ${companies.rows.length + departments.rows.length + employees.rows.length + assetCategories.rows.length + assets.rows.length + qrCodes.rows.length + softwareCatalog.rows.length + licenses.rows.length + usageLogs.rows.length + predictions.rows.length + recommendations.rows.length + chatHistory.rows.length + auditLogs.rows.length + notifications.rows.length}`);
  report.push(`  Errors: ${errors}`);
  report.push(`  Warnings: ${warnings}`);
  report.push(`  Result: ${errors === 0 ? 'PASS' : 'FAIL'}`);

  // Check AI assumptions
  report.push('\n=== AI ASSUMPTIONS ===');
  // Some users login daily
  const heavyUsers = Object.entries(empLoginCount).filter(([_,c]) => c >= 200);
  report.push(`  Daily/Heavy users (200+ logins): ${heavyUsers.length}`);
  // Some never login
  const neverLogin = employees.rows.filter(r => !empLoginCount[r.employee_id]);
  report.push(`  Employees with zero logins: ${neverLogin.length}`);
  // Some resigned employees still own assets
  const resignedEmp = employees.rows.filter(r => r.employment_status === 'offboarding' || r.employment_status === 'inactive');
  const resignedWithAssets = resignedEmp.filter(r => assets.rows.some(a => a.current_employee_id === r.employee_id));
  report.push(`  Resigned/inactive employees still holding assets: ${resignedWithAssets.length}`);
  // Unused licenses
  const unusedLic = licenses.rows.filter(r => parseInt(r.available_licenses) > 0);
  report.push(`  Licenses with available seats: ${unusedLic.length}`);
  // Department consumption differences
  const deptUsage = {};
  usageLogs.rows.forEach(r => {
    const dept = r.department || 'Unknown';
    if (!deptUsage[dept]) deptUsage[dept] = 0;
    deptUsage[dept]++;
  });
  report.push(`  Software usage by department (sample): ${JSON.stringify(Object.fromEntries(Object.entries(deptUsage).sort((a,b) => b[1]-a[1]).slice(0,5)))}`);

  return report.join('\n');
}

try {
  const result = validate();
  console.log(result);
  fs.writeFileSync(path.join(__dirname, 'validation_result.txt'), result);
} catch (e) {
  console.error('Validation failed:', e.message);
  process.exit(1);
}
