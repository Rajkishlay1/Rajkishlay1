import requests, time, sys, os
from datetime import datetime
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ENDPOINTS = [
    {
        "name": "SolarHub Dashboard",
        "url": "https://solarhub.involtics.com",
        "target_ip": "65.1.116.16",
        "type": "INVENTA DASHBOARD (3kW 1p)",
        "critical": True,
        "expected": [200, 301, 302]
    },
    {
        "name": "DB Demo API Docs",
        "url": "https://dbdemo.involtics.com/api/docs/",
        "target_ip": "3.7.128.202",
        "type": "INVENTA DATABASE (S2)",
        "critical": True,
        "expected": [200, 301, 302]
    },
    {
        "name": "Involtics Main Site",
        "url": "https://involtics.com",
        "target_ip": "65.2.104.2",
        "type": "COMPANY PORTAL",
        "critical": True,
        "expected": [200, 301, 302]
    },
    {
        "name": "Watthut Main Site",
        "url": "https://watthut.com",
        "target_ip": "65.2.104.2",
        "type": "WATTHUT PORTAL",
        "critical": True,
        "expected": [200, 301, 302]
    },
    {
        "name": "Watthut Involtics Portal",
        "url": "https://watthut.com/involtics.com",
        "target_ip": "65.2.104.2",
        "type": "INTEGRATION PORTAL",
        "critical": True,
        "expected": [200, 301, 302]
    },
    {
        "name": "RMS India App",
        "url": "https://rmsindapp.involtics.com",
        "target_ip": "35.154.17.98",
        "type": "INDIA DATA CENTER APP",
        "critical": False,
        "expected": [200, 301, 302]
    },
    {
        "name": "RMS Global App",
        "url": "https://rmsapp.involtics.com",
        "target_ip": "35.154.17.98",
        "type": "RMS APP",
        "critical": False,
        "expected": [200, 301, 302]
    },
    {
        "name": "RAMS Database",
        "url": "https://rmsdb.involtics.com",
        "target_ip": "35.154.17.98",
        "type": "DATABASE SERVER",
        "critical": False,
        "expected": [200, 301, 302]
    }
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 InvolticsProductionMonitor/2.0"
}

results = []
critical_failures = 0

print("=" * 105)
print("INVOLTICS & WATTHUT PRODUCTION FLEET MONITOR")
print("=" * 105)
print(f"{'Service Name':<25} | {'Server IP':<15} | {'URL':<35} | {'Status':<12} | {'Time (s)':<8}")
print("-" * 105)

for ep in ENDPOINTS:
    name = ep["name"]
    url = ep["url"]
    ip = ep["target_ip"]
    expected = ep["expected"]
    is_crit = ep["critical"]
    
    status_str = ""
    time_str = ""
    is_ok = False
    
    start = time.time()
    try:
        r = requests.get(url, headers=HEADERS, timeout=8, allow_redirects=True, verify=False)
        elapsed = time.time() - start
        time_str = f"{elapsed:.3f}s"
        status_code = r.status_code
        
        if status_code in expected:
            status_str = f"✅ HTTP {status_code}"
            is_ok = True
        else:
            status_str = f"⚠️ HTTP {status_code}"
            is_ok = False
            
    except requests.exceptions.Timeout:
        elapsed = time.time() - start
        time_str = f">{elapsed:.1f}s"
        status_str = "❌ TIMEOUT"
        is_ok = False
    except Exception as ex:
        elapsed = time.time() - start
        time_str = f"{elapsed:.2f}s"
        err_msg = str(ex)
        if "522" in err_msg:
            status_str = "❌ CF 522"
        elif "NameResolutionError" in err_msg or "Failed to resolve" in err_msg:
            status_str = "❌ DNS UNRESOLVED"
        else:
            status_str = "❌ CONN ERR"
        is_ok = False
        
    if is_crit and not is_ok:
        critical_failures += 1
        
    print(f"{name:<25} | {ip:<15} | {url:<35} | {status_str:<12} | {time_str:<8}")
    results.append({
        "name": name,
        "type": ep["type"],
        "ip": ip,
        "url": url,
        "status": status_str,
        "time": time_str,
        "ok": is_ok,
        "critical": is_crit
    })

print("=" * 105)
print(f"Summary: {len(results)} services checked. Critical Failures: {critical_failures}")

# Generate GitHub Step Summary markdown if running inside GitHub Actions
summary_file = os.getenv("GITHUB_STEP_SUMMARY")
now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")

md = f"""# 🛡️ Involtics & Watthut Production Fleet Status

> **Audit Timestamp:** `{now_str}`  
> **Total Monitored Endpoints:** `{len(results)}`  
> **Critical Production Status:** `{'🟢 ALL OPERATIONAL' if critical_failures == 0 else '🚨 CRITICAL OUTAGE DETECTED'}`

### 📊 Service Health Matrix

| Service | Server IP | Role | Status | Response Time |
|---|---|---|---|---|
"""
for r in results:
    md += f"| **[{r['name']}]({r['url']})** | `{r['ip']}` | {r['type']} | {r['status']} | `{r['time']}` |\n"

md += """
---
### 📌 Server Infrastructure Mapping
- **65.1.116.16:** SolarHub Dashboard (`solarhub.involtics.com`) — Inventa Dashboard + String + 3kW 1p
- **3.7.128.202 (S2):** DB Demo (`dbdemo.involtics.com`) — Inventa Database + Telemetry Pipeline
- **65.2.104.2:** Company Gateways (`involtics.com`, `watthut.com`, `watthut.com/involtics.com`)
- **35.154.17.98:** India Data Center Core (`rmsdb.involtics.com`, `rmsindapp.involtics.com`, `rmsapp.involtics.com`)
"""

if summary_file:
    with open(summary_file, "a", encoding="utf-8") as f:
        f.write(md)

if critical_failures > 0:
    print("\n🚨 CRITICAL ALERT: One or more primary production services failed!")
    sys.exit(1)
else:
    print("\n✅ All critical production services are HEALTHY!")
    sys.exit(0)
