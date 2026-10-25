from requests import get
import csv, time, socket

def get_rdns(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except:
        return "N/A"

def check_ip_api(ip=""):
    url = f"http://ip-api.com/json/{ip}?fields=status,query,city,regionName,country,isp,org,proxy,hosting,mobile,lat,lon,timezone,zip"
    try:
        r = get(url, timeout=10).json()
        if r.get("status") != "success":
            return None
        r.pop("status", None)
        r["rdns"] = get_rdns(r["query"]) if ip else "N/A"
        return r
    except:
        return None

print("=== HexSec Ultimate IP Checker ===")
eingabe = input("IP(s) mit Komma: ").strip()
ips = [x.strip() for x in eingabe.replace("\n",",").split(",") if x.strip()] if eingabe else [""]

results = []
for ip in ips:
    print(f"\n🔍 Checking {ip if ip else 'meine IP'}...")
    data = check_ip_api(ip)
    if not data: continue
    
    risk = []
    if data.get("proxy"): risk.append("🔴 PROXY/VPN")
    if data.get("hosting"): risk.append("☁️ HOSTING/DC")
    if data.get("mobile"): risk.append("📱 MOBILE")
    risk_str = " | ".join(risk) if risk else "🟢 Residential/Clean"

    print(f"""
🌐 IP: {data['query']} ({data['rdns']})
📍 {data.get('city')} {data.get('zip')}, {data.get('regionName')}, {data.get('country')}
🏢 {data.get('isp')} / {data.get('org')}
⏰ {data.get('timezone')} | {data.get('lat')},{data.get('lon')}
🚨 RISK: {risk_str}
    """)
    results.append(data)
    time.sleep(1.5)

if results:
    with open("results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    html = """<html><head><title>IP Map</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>#map{height:100vh;margin:0}body{margin:0}</style></head><body><div id="map"></div>
<script>
var map = L.map('map').setView([20,0],2);
// ESRI - braucht keinen API Key und blockt nicht
L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}', {
 attribution: '© Esri © OpenStreetMap',
 maxZoom: 19
}).addTo(map);
"""
    for d in results:
        html += f"L.marker([{d['lat']},{d['lon']}]).addTo(map).bindPopup(\"{d['query']}<br>{d.get('city')}, {d.get('country')}<br>{d.get('isp')}\");\n"
    html += "</script></body></html>"
    
    with open("map.html", "w") as f:
        f.write(html)
    
    print(f"\n✅ {len(results)} IPs gespeichert!")
    print("📄 results.csv")
    print("🗺️ map.html - DIESMAL 100% FIXED mit ESRI Tiles!")
