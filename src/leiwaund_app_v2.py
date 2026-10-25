import customtkinter as ctk
import requests
import socket
import subprocess
import threading
import re
import csv
import os
from datetime import datetime
import time
import platform

COMMON_PORTS = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
    80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS",
    3306: "MySQL", 3389: "RDP", 5432: "Postgres",
    6379: "Redis", 8080: "HTTP-Alt", 27017: "MongoDB"
}

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class LeiwaundOSApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("LeiwaundOS v2.0 // FULL")
        self.geometry("950x750")
        self.header = ctk.CTkLabel(self, text="SYS::LEIWAUND_OS v2.0 // FULL PROTOCOL", font=("Courier", 20, "bold"), text_color="#00fff0")
        self.header.pack(pady=10)
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.pack(fill="x", padx=20, pady=5)
        self.ip_entry = ctk.CTkEntry(self.input_frame, placeholder_text="IP oder Domain z.B. 8.8.8.8", width=400, font=("Courier", 14))
        self.ip_entry.pack(side="left", padx=10, pady=10)
        self.ip_entry.bind("<Return>", lambda e: self.scan_all())
        self.btn_all = ctk.CTkButton(self.input_frame, text="🔥 SCAN ALLES", command=self.scan_all, fg_color="#ff00a0", hover_color="#cc0080")
        self.btn_all.pack(side="left", padx=5)
        self.btn_map = ctk.CTkButton(self.input_frame, text="🗺️ MAP", command=self.open_map, width=80)
        self.btn_map.pack(side="left", padx=5)
        self.tabs = ctk.CTkTabview(self, width=900, height=600)
        self.tabs.pack(padx=20, pady=10, fill="both", expand=True)
        self.tab_info = self.tabs.add("INFO")
        self.tab_ports = self.tabs.add("PORTS")
        self.tab_trace = self.tabs.add("TRACE")
        self.tab_whois = self.tabs.add("WHOIS")
        self.tab_ping = self.tabs.add("PING")
        self.tab_log = self.tabs.add("LOG")
        self.info_box = ctk.CTkTextbox(self.tab_info, font=("Courier", 12))
        self.info_box.pack(fill="both", expand=True, padx=5, pady=5)
        self.info_box.insert("0.0", ">> LeiwaundOS bereit. IP eingeben und SCAN ALLES drücken...\n")
        self.ports_box = ctk.CTkTextbox(self.tab_ports, font=("Courier", 12))
        self.ports_box.pack(fill="both", expand=True, padx=5, pady=5)
        self.trace_box = ctk.CTkTextbox(self.tab_trace, font=("Courier", 11))
        self.trace_box.pack(fill="both", expand=True, padx=5, pady=5)
        self.whois_box = ctk.CTkTextbox(self.tab_whois, font=("Courier", 11))
        self.whois_box.pack(fill="both", expand=True, padx=5, pady=5)
        self.ping_frame = ctk.CTkFrame(self.tab_ping)
        self.ping_frame.pack(fill="x", padx=5, pady=5)
        self.ping_btn = ctk.CTkButton(self.ping_frame, text="📶 PING 10x", command=self.do_ping)
        self.ping_btn.pack(side="left", padx=10, pady=10)
        self.ping_result = ctk.CTkLabel(self.ping_frame, text="Avg: - ms | Loss: -", font=("Courier", 12))
        self.ping_result.pack(side="left", padx=20)
        self.ping_box = ctk.CTkTextbox(self.tab_ping, font=("Courier", 12))
        self.ping_box.pack(fill="both", expand=True, padx=5, pady=5)
        self.log_box = ctk.CTkTextbox(self.tab_log, font=("Courier", 10))
        self.log_box.pack(fill="both", expand=True, padx=5, pady=5)
        self.target_ip = ""
        self.last_data = {}
    def log(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_box.insert("end", f"[{ts}] {msg}\n")
        self.log_box.see("end")
    def scan_all(self):
        ip = self.ip_entry.get().strip()
        if not ip: return
        try:
            if not re.match(r"^\d+\.\d+\.\d+\.\d+$", ip):
                ip_resolved = socket.gethostbyname(ip)
                self.log(f"Domain {ip} -> {ip_resolved}")
                self.target_ip = ip_resolved
            else:
                self.target_ip = ip
        except Exception as e:
            self.target_ip = ip
            self.log(f"Resolve Fehler: {e}")
        self.info_box.delete("0.0", "end")
        self.info_box.insert("0.0", f">> Scanning {self.target_ip}...\n")
        threading.Thread(target=self._scan_info, daemon=True).start()
        threading.Thread(target=self._scan_ports, daemon=True).start()
        threading.Thread(target=self._scan_trace, daemon=True).start()
        threading.Thread(target=self._scan_whois, daemon=True).start()
        threading.Thread(target=self._scan_ping, daemon=True).start()
    def _scan_info(self):
        try:
            self.log(f"INFO: Abfrage {self.target_ip}")
            r = requests.get(f"http://ip-api.com/json/{self.target_ip}?fields=status,message,country,regionName,city,lat,lon,isp,org,as,query,reverse", timeout=10).json()
            if r.get("status") == "fail":
                txt = f"Fail: {r.get('message')}"
            else:
                txt = f"IP: {r.get('query')}\nReverse: {r.get('reverse')}\nLand: {r.get('country')} - {r.get('regionName')} - {r.get('city')}\nLat/Lon: {r.get('lat')} / {r.get('lon')}\nISP: {r.get('isp')}\nORG: {r.get('org')}\nAS: {r.get('as')}\n\n>> MAP generiert...\n"
                self.last_data = r
                self._gen_map(r)
                self._save_history(r)
            self.info_box.delete("0.0", "end")
            self.info_box.insert("0.0", txt)
            self.log("INFO: Fertig")
        except Exception as e:
            self.info_box.insert("end", f"\nFehler: {e}")
            self.log(f"INFO Fehler: {e}")
    def _gen_map(self, data):
        try:
            lat, lon = data.get("lat"), data.get("lon")
            html = f"<html><head><link rel=\"stylesheet\" href=\"https://unpkg.com/leaflet@1.9.4/dist/leaflet.css\"/><script src=\"https://unpkg.com/leaflet@1.9.4/dist/leaflet.js\"></script><style>body{{margin:0;background:#0a0e2a}} #map{{height:100vh}} .info{{position:absolute;top:10px;left:50px;z-index:999;background:#0a0e2ae0;color:#00fff0;padding:10px;border:1px solid #ff00a0;font-family:monospace}}</style></head><body><div class=\"info\">{data.get('query')} - {data.get('city')} - {data.get('isp')}</div><div id=\"map\"></div><script>var m=L.map('map').setView([{lat},{lon}],10);L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{y}}/{{x}}.png').addTo(m);L.marker([{lat},{lon}]).addTo(m).bindPopup(\"{data.get('query')}\").openPopup();L.circle([{lat},{lon}],{{radius:5000,color:'#ff00a0',fillColor:'#ff00a0',fillOpacity:0.2}}).addTo(m);</script></body></html>"
            path = os.path.expanduser("~/Schreibtisch/LeiwaundOS-App/output/map.html")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f: f.write(html)
        except Exception as e: self.log(f"MAP Fehler: {e}")
    def _scan_ports(self):
        self.ports_box.delete("0.0", "end")
        self.ports_box.insert("0.0", f">> Port Scan {self.target_ip} läuft...\n\n")
        self.log(f"PORTS: Scan {self.target_ip}")
        open_ports = []
        for port, name in COMMON_PORTS.items():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.8)
                res = s.connect_ex((self.target_ip, port))
                if res == 0:
                    line = f"[OPEN] {port:5} / {name:12}\n"
                    self.ports_box.insert("end", line)
                    open_ports.append(port)
                else:
                    self.ports_box.insert("end", f"[....] {port:5} / {name:12} closed\n")
                s.close()
                self.ports_box.see("end")
            except Exception as e:
                self.ports_box.insert("end", f"[ERR ] {port} {e}\n")
        self.ports_box.insert("end", f"\n>> Fertig. {len(open_ports)} offene Ports: {open_ports}\n")
        self.log(f"PORTS: {len(open_ports)} offen")
    def _scan_trace(self):
        self.trace_box.delete("0.0", "end")
        self.trace_box.insert("0.0", f">> Traceroute zu {self.target_ip}...\n\n")
        self.log(f"TRACE: Starte")
        try:
            cmd = ["traceroute", "-m", "20", "-w", "1", self.target_ip] if platform.system() != "Windows" else ["tracert", "-h", "20", self.target_ip]
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in proc.stdout:
                self.trace_box.insert("end", line)
                self.trace_box.see("end")
                self.update_idletasks()
            self.log("TRACE: Fertig")
        except Exception as e:
            self.trace_box.insert("end", f"Fehler: {e}")
    def _scan_whois(self):
        self.whois_box.delete("0.0", "end")
        self.whois_box.insert("0.0", f">> WHOIS {self.target_ip}...\n\n")
        self.log("WHOIS: Abfrage")
        try:
            out = subprocess.check_output(["whois", self.target_ip], timeout=10, text=True, stderr=subprocess.STDOUT)
            self.whois_box.insert("end", out[:8000])
            self.log("WHOIS: Fertig")
        except Exception as e:
            self.whois_box.insert("end", f"Fehler: {e}")
    def _scan_ping(self): self.do_ping()
    def do_ping(self):
        self.ping_box.delete("0.0", "end")
        self.ping_box.insert("0.0", f">> Ping {self.target_ip} 10x...\n\n")
        times = []
        try:
            for i in range(10):
                try:
                    out = subprocess.check_output(["ping", "-c", "1", "-W", "1", self.target_ip], text=True, timeout=2)
                    m = re.search(r"time=([\d\.]+) ms", out)
                    if m:
                        t = float(m.group(1))
                        times.append(t)
                        bar = "█" * int(t/10) if t < 100 else "█"*10 + "!"
                        self.ping_box.insert("end", f"[{i+1:2}] {t:6.2f} ms {bar}\n")
                    else:
                        self.ping_box.insert("end", f"[{i+1:2}] timeout\n")
                except subprocess.CalledProcessError:
                    self.ping_box.insert("end", f"[{i+1:2}] no reply\n")
                self.ping_box.see("end")
                self.update()
                time.sleep(0.2)
            if times:
                avg = sum(times)/len(times)
                self.ping_result.configure(text=f"Avg: {avg:.1f} ms | Min: {min(times):.1f} | Max: {max(times):.1f} | Loss: {10-len(times)}/10")
                self.ping_box.insert("end", f"\n>> Durchschnitt: {avg:.2f} ms\n")
                self.log(f"PING: Avg {avg:.1f}ms")
        except Exception as e:
            self.ping_box.insert("end", f"Fehler: {e}")
    def _save_history(self, data):
        try:
            path = os.path.expanduser("~/Schreibtisch/LeiwaundOS-App/output/history.csv")
            exists = os.path.exists(path)
            with open(path, "a", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                if not exists: w.writerow(["timestamp", "ip", "city", "country", "isp", "lat", "lon"])
                w.writerow([datetime.now().isoformat(), data.get("query"), data.get("city"), data.get("country"), data.get("isp"), data.get("lat"), data.get("lon")])
            self.log(f"History gespeichert: {path}")
        except Exception as e: self.log(f"History Fehler: {e}")

    def open_map(self, lat=None, lon=None, ip=None, city=None):
        try:
            if lat is None:
                lat = getattr(self, 'current_lat', None) or self.last_data.get('lat')
            if lon is None:
                lon = getattr(self, 'current_lon', None) or self.last_data.get('lon')
            if ip is None:
                ip = getattr(self, 'current_ip', None) or self.last_data.get('query') or '8.8.8.8'
            if city is None:
                city = getattr(self, 'current_city', None) or self.last_data.get('city') or 'Unknown'
            if lat is None or lon is None:
                self.log('MAP: Keine Koordinaten - erst IP scannen!')
                return
            import webbrowser
            # Direkt OSM Website - geht IMMER, braucht keinen Key, keine Tiles
            url = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=13/{lat}/{lon}"
            webbrowser.open(url)
            # Zweiter Tab mit Google Maps als Fallback
            # webbrowser.open(f"https://www.google.com/maps/search/?api=1&query={lat},{lon}")
            self.log(f'MAP: OSM geöffnet {city} {lat},{lon} - im Browser')
        except Exception as e:
            self.log(f'MAP Fehler: {e}')



if __name__ == "__main__":
    app = LeiwaundOSApp()
    app.mainloop()
