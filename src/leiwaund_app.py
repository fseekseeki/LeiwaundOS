import customtkinter as ctk
import requests, socket, csv, webbrowser, os
from threading import Thread

BG = "#0a0e2a"
CARD = "#131a4a"
PINK = "#ff00a0"
CYAN = "#00fff0"
WHITE = "#ffffff"

ctk.set_appearance_mode("dark")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("LeiwaundOS - IP Checker")
        self.geometry("650x750")
        self.configure(fg_color=BG)
        try: self.iconphoto(True, ctk.CTkImage)
        except: pass
        
        self.results = []

        # Title
        tf = ctk.CTkFrame(self, fg_color="transparent")
        tf.pack(pady=15)
        ctk.CTkLabel(tf, text="Leiwa", font=("Orbitron", 38, "bold"), text_color=PINK).pack(side="left")
        ctk.CTkLabel(tf, text="und", font=("Orbitron", 38, "bold"), text_color=WHITE).pack(side="left")
        ctk.CTkLabel(tf, text="OS", font=("Orbitron", 38, "bold"), text_color=CYAN).pack(side="left")
        ctk.CTkLabel(self, text="IP CHECKER // SYS::SECURE ONLINE", font=("Consolas", 11), text_color=CYAN).pack()

        # Input
        card = ctk.CTkFrame(self, fg_color=CARD, border_color=PINK, border_width=2, corner_radius=15)
        card.pack(pady=15, padx=20, fill="x")
        ctk.CTkLabel(card, text="IP(s) mit Komma:", font=("Consolas", 12), text_color=WHITE).pack(anchor="w", padx=15, pady=(12,5))
        self.entry = ctk.CTkEntry(card, placeholder_text="8.8.8.8, 1.1.1.1, 3.3.3.3", fg_color=BG, border_color=CYAN, text_color=WHITE, height=45, font=("Consolas", 13))
        self.entry.pack(fill="x", padx=15, pady=5)
        self.btn = ctk.CTkButton(card, text="SCAN STARTEN", command=self.start_scan, fg_color=PINK, hover_color="#cc0080", height=42, font=("Orbitron", 13, "bold"))
        self.btn.pack(fill="x", padx=15, pady=12)

        # Action Buttons
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=5)
        ctk.CTkButton(btn_row, text="🗺️ Karte öffnen", command=self.open_map, fg_color=CARD, border_color=CYAN, border_width=1, width=150).pack(side="left", padx=5)
        ctk.CTkButton(btn_row, text="📄 CSV Export", command=self.export_csv, fg_color=CARD, border_color=PINK, border_width=1, width=150).pack(side="left", padx=5)
        ctk.CTkLabel(btn_row, text="PROTOCOL v2.87", font=("Consolas", 9), text_color=PINK).pack(side="right")

        # Results
        self.box = ctk.CTkTextbox(self, fg_color=CARD, text_color=WHITE, border_color=CYAN, border_width=1, font=("Consolas", 11), height=400)
        self.box.pack(pady=10, padx=20, fill="both", expand=True)

    def log(self, t): 
        self.box.insert("end", t+"\n")
        self.box.see("end")

    def get_rdns(self, ip):
        try: return socket.gethostbyaddr(ip)[0]
        except: return "N/A"

    def check(self, ip):
        try:
            r = requests.get(f"http://ip-api.com/json/{ip}?fields=status,query,city,country,isp,org,proxy,hosting,lat,lon", timeout=10).json()
            if r.get("status")!="success": return None
            r["rdns"]=self.get_rdns(r["query"])
            risk = []
            if r.get("proxy"): risk.append("PROXY/VPN")
            if r.get("hosting"): risk.append("HOSTING/DC")
            r["risk"]=" | ".join(risk) if risk else "CLEAN"
            return r
        except: return None

    def start_scan(self):
        raw = self.entry.get().strip()
        ips = [x.strip() for x in raw.split(",") if x.strip()] if raw else [""]
        self.box.delete("1.0","end")
        self.results=[]
        self.log(f"🔍 Scanning {len(ips)} IP(s)...\n")
        def run():
            for ip in ips:
                d=self.check(ip)
                if not d: continue
                self.results.append(d)
                self.log(f"🌐 {d['query']} ({d['rdns']})\n📍 {d.get('city')}, {d.get('country')} | {d.get('lat')},{d.get('lon')}\n🏢 {d.get('isp')}\n🚨 RISK: {d['risk']}\n{'-'*45}")
            self.log("\n✅ DONE - Leiwand!")
            self.make_map()
        Thread(target=run, daemon=True).start()

    def make_map(self):
        if not self.results: return
        html=f"""<html><head><title>LeiwaundOS Map</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>#map{{height:100vh;margin:0}}body{{margin:0;background:#0a0e2a}}</style></head><body><div id="map"></div>
<script>var map=L.map('map').setView([20,0],2);
L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{{z}}/{{y}}/{{x}}',{{maxZoom:19}}).addTo(map);
"""
        for d in self.results:
            html+=f"L.marker([{d['lat']},{d['lon']}]).addTo(map).bindPopup(\"{d['query']}<br>{d.get('city')}<br>{d.get('isp')}\");\n"
        html+="</script></body></html>"
        with open("map.html","w") as f: f.write(html)

    def open_map(self):
        if os.path.exists("map.html"): webbrowser.open("file://"+os.path.abspath("map.html"))
        else: self.log("⚠️ Erst scannen!")

    def export_csv(self):
        if not self.results: self.log("⚠️ Nix zum exportieren"); return
        with open("results.csv","w",newline="",encoding="utf-8") as f:
            w=csv.DictWriter(f, fieldnames=self.results[0].keys()); w.writeheader(); w.writerows(self.results)
        self.log("📄 results.csv gespeichert!")

if __name__=="__main__":
    App().mainloop()
