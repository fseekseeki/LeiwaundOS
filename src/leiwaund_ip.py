import customtkinter as ctk
import requests, socket, csv
from threading import Thread

# LeiwaundOS Colors
BG = "#0a0e2a"
CARD = "#131a4a"
PINK = "#ff00a0"
CYAN = "#00fff0"
WHITE = "#ffffff"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class LeiwaundIP(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("LeiwaundOS - IP Checker")
        self.geometry("600x700")
        self.configure(fg_color=BG)

        # TITLE - LeiwaundOS Style
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(pady=20)

        # Leiwa (pink) + und (white) + OS (cyan)
        ctk.CTkLabel(title_frame, text="Leiwa", font=("Orbitron", 36, "bold"), text_color=PINK).pack(side="left")
        ctk.CTkLabel(title_frame, text="und", font=("Orbitron", 36, "bold"), text_color=WHITE).pack(side="left")
        ctk.CTkLabel(title_frame, text="OS", font=("Orbitron", 36, "bold"), text_color=CYAN).pack(side="left")

        ctk.CTkLabel(self, text="IP CHECKER // SYS::SECURE ONLINE", font=("Consolas", 12), text_color=CYAN).pack()

        # Input Card
        card = ctk.CTkFrame(self, fg_color=CARD, border_color=PINK, border_width=2, corner_radius=15)
        card.pack(pady=20, padx=20, fill="x")

        ctk.CTkLabel(card, text="IP(s) mit Komma:", font=("Consolas", 13), text_color=WHITE).pack(anchor="w", padx=15, pady=(15,5))
        
        self.entry = ctk.CTkEntry(card, placeholder_text="z.B. 8.8.8.8, 1.1.1.1", 
                                  fg_color=BG, border_color=CYAN, text_color=WHITE,
                                  height=45, font=("Consolas", 14))
        self.entry.pack(fill="x", padx=15, pady=5)

        self.btn = ctk.CTkButton(card, text="SCAN STARTEN", command=self.start_scan,
                                 fg_color=PINK, hover_color="#cc0080", text_color=WHITE,
                                 height=45, font=("Orbitron", 14, "bold"))
        self.btn.pack(fill="x", padx=15, pady=15)

        # Results
        self.result_box = ctk.CTkTextbox(self, fg_color=CARD, text_color=WHITE,
                                         border_color=CYAN, border_width=1,
                                         font=("Consolas", 12), height=350)
        self.result_box.pack(pady=10, padx=20, fill="both", expand=True)

        # Footer
        ctk.CTkLabel(self, text="PROTOCOL v2.87 // PORT SCAN ACTIVE", font=("Consolas", 10), text_color=PINK).pack(pady=10)

    def log(self, txt, color=None):
        self.result_box.insert("end", txt + "\n")
        self.result_box.see("end")

    def get_rdns(self, ip):
        try: return socket.gethostbyaddr(ip)[0]
        except: return "N/A"

    def check_one(self, ip):
        try:
            url = f"http://ip-api.com/json/{ip}?fields=status,query,city,regionName,country,isp,org,proxy,hosting,lat,lon,timezone"
            r = requests.get(url, timeout=10).json()
            if r.get("status") != "success": return
            rdns = self.get_rdns(r["query"])
            
            risk = []
            if r.get("proxy"): risk.append("PROXY/VPN")
            if r.get("hosting"): risk.append("HOSTING/DC")
            risk_str = " | ".join(risk) if risk else "CLEAN"

            self.log(f"\n🌐 {r['query']} ({rdns})")
            self.log(f"📍 {r.get('city')}, {r.get('country')} | {r.get('lat')},{r.get('lon')}")
            self.log(f"🏢 {r.get('isp')}")
            self.log(f"🚨 RISK: {risk_str}")
            self.log("-"*40)
        except Exception as e:
            self.log(f"Error {ip}: {e}")

    def start_scan(self):
        ips_raw = self.entry.get().strip()
        ips = [x.strip() for x in ips_raw.split(",") if x.strip()] if ips_raw else [""]
        self.result_box.delete("1.0", "end")
        self.log(f"🔍 Scanning {len(ips)} IP(s)...\n")
        def run():
            for ip in ips:
                self.check_one(ip)
            self.log("\n✅ DONE - Leiwand!")
        Thread(target=run, daemon=True).start()

if __name__ == "__main__":
    app = LeiwaundIP()
    app.mainloop()
