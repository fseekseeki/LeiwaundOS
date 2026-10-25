import subprocess, datetime, pathlib, os
from PIL import ImageGrab
import customtkinter as ctk

# Für Linux: gnome-screenshot nutzen
def shot():
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out = pathlib.Path.home() / f"Schreibtisch/LeiwaundOS_screenshot_{ts}.png"
    subprocess.run(["gnome-screenshot", "-a", "-f", str(out)])  # -a = Bereich wählen
    print(f"Saved: {out}")

if __name__ == "__main__":
    shot()
