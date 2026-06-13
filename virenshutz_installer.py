import os
import json
import base64

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPS = os.path.join(BASE, "apps")
IMG = os.path.join(BASE, "images")
APPDATA = os.path.join(APPS, "appdata", "bdlass_defender")
APPS_INFO = os.path.join(APPS, "apps_info.json")
SHORTCUTS = os.path.join(BASE, "shortcuts.json")
APPS_CFG = os.path.join(APPS, "apps_config.json")
DEFENDER_CFG = os.path.join(APPDATA, "config.json")

def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            d = f.read().strip()
            return json.loads(d) if d else default
    except:
        return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# 1. AppData + Config
os.makedirs(APPDATA, exist_ok=True)
os.makedirs(os.path.join(APPDATA, "quarantaene"), exist_ok=True)

if not os.path.exists(DEFENDER_CFG):
    save_json(DEFENDER_CFG, {"pro": False})

# 2. BDLASS Defender App schreiben
virenschutz_code = r'''
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import json
import hashlib
import time
import shutil

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPS = os.path.join(BASE, "apps")
APPDATA = os.path.join(APPS, "appdata", "bdlass_defender")
QUAR = os.path.join(APPDATA, "quarantaene")
CFG = os.path.join(APPDATA, "config.json")

SUSPICIOUS_EXT = [".exe", ".bat", ".cmd", ".vbs", ".js", ".scr"]

def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            d = f.read().strip()
            return json.loads(d) if d else default
    except:
        return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

class BDLASSDefender:
    def __init__(self):
        os.makedirs(APPDATA, exist_ok=True)
        os.makedirs(QUAR, exist_ok=True)

        self.cfg = load_json(CFG, {"pro": False})

        self.root = tk.Tk()
        self.root.title("BDLASS Defender")
        self.root.geometry("900x550")
        self.root.configure(bg="#202020")

        left = tk.Frame(self.root, bg="#202020")
        left.pack(side="left", fill="y", padx=10, pady=10)

        right = tk.Frame(self.root, bg="#202020")
        right.pack(side="right", expand=True, fill="both", padx=10, pady=10)

        tk.Label(left, text="BDLASS Defender", bg="#202020", fg="white",
                 font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=5)

        self.mode_label = tk.Label(left, bg="#202020", fg="white",
                                   font=("Segoe UI", 10))
        self.mode_label.pack(anchor="w", pady=5)

        tk.Button(left, text="Schnellscan", bg="#404040", fg="white",
                  command=self.quick_scan).pack(fill="x", pady=3)

        tk.Button(left, text="Ordner scannen", bg="#404040", fg="white",
                  command=self.folder_scan).pack(fill="x", pady=3)

        tk.Button(left, text="Quarantäne öffnen", bg="#404040", fg="white",
                  command=self.open_quarantine).pack(fill="x", pady=3)

        tk.Button(left, text="BDLASS Defender Upgrade", bg="#3a7bd5", fg="white",
                  command=self.upgrade).pack(fill="x", pady=10)

        self.log = tk.Text(right, bg="#101010", fg="#00ff00",
                           font=("Consolas", 9))
        self.log.pack(expand=True, fill="both")

        self.update_mode_label()
        self.log_write("BDLASS Defender gestartet.\n")

        self.root.mainloop()

    def update_mode_label(self):
        if self.cfg.get("pro"):
            self.mode_label.config(text="Modus: Pro-Schutz (C-Level)")
        else:
            self.mode_label.config(text="Modus: Standard-Schutz (B-Level)")

    def log_write(self, text):
        self.log.insert("end", text)
        self.log.see("end")
        self.root.update_idletasks()

    def hash_file(self, path):
        h = hashlib.sha256()
        try:
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    h.update(chunk)
            return h.hexdigest()
        except:
            return "ERROR"

    def scan_path(self, root_path):
        suspicious = []
        for dirpath, dirnames, filenames in os.walk(root_path):
            for name in filenames:
                full = os.path.join(dirpath, name)
                ext = os.path.splitext(name)[1].lower()
                if ext in SUSPICIOUS_EXT:
                    suspicious.append(full)
        return suspicious

    def quick_scan(self):
        self.log_write("\n[Schnellscan] Starte Scan...\n")
        target = BASE
        suspicious = self.scan_path(target)

        if not suspicious:
            self.log_write("Keine verdächtigen Dateien gefunden.\n")
            return

        self.log_write(f"{len(suspicious)} verdächtige Dateien gefunden:\n")
        for f in suspicious:
            if self.cfg.get("pro"):
                h = self.hash_file(f)
                size = os.path.getsize(f)
                self.log_write(f"- {f} | {size} Bytes | SHA256: {h}\n")
            else:
                self.log_write(f"- {f}\n")

        self.ask_quarantine(suspicious)

    def folder_scan(self):
        path = filedialog.askdirectory()
        if not path:
            return
        self.log_write(f"\n[Ordner-Scan] Starte Scan in: {path}\n")
        suspicious = self.scan_path(path)

        if not suspicious:
            self.log_write("Keine verdächtigen Dateien gefunden.\n")
            return

        self.log_write(f"{len(suspicious)} verdächtige Dateien gefunden:\n")
        for f in suspicious:
            if self.cfg.get("pro"):
                h = self.hash_file(f)
                size = os.path.getsize(f)
                self.log_write(f"- {f} | {size} Bytes | SHA256: {h}\n")
            else:
                self.log_write(f"- {f}\n")

        self.ask_quarantine(suspicious)

    def ask_quarantine(self, files):
        if not files:
            return
        if not messagebox.askyesno("Quarantäne", "Verdächtige Dateien in Quarantäne verschieben?"):
            self.log_write("Benutzer hat Quarantäne abgelehnt.\n")
            return

        for f in files:
            try:
                base = os.path.basename(f)
                target = os.path.join(QUAR, f"{int(time.time())}_{base}")
                shutil.move(f, target)
                self.log_write(f"In Quarantäne verschoben: {f}\n")
            except Exception as e:
                self.log_write(f"Fehler bei Quarantäne: {f} ({e})\n")

    def open_quarantine(self):
        self.log_write(f"\nQuarantäne-Ordner: {QUAR}\n")
        try:
            os.startfile(QUAR)
        except:
            self.log_write("Konnte Quarantäne-Ordner nicht öffnen.\n")

    def upgrade(self):
        if self.cfg.get("pro"):
            messagebox.showinfo("BDLASS Defender", "Pro-Schutz ist bereits aktiviert.")
            return

        self.cfg["pro"] = True
        save_json(CFG, self.cfg)
        self.update_mode_label()
        self.log_write("\n[Upgrade] Pro-Schutz (C-Level) aktiviert.\n")
        messagebox.showinfo("BDLASS Defender", "Upgrade erfolgreich! Pro-Schutz (C-Level) ist jetzt aktiv.")

if __name__ == "__main__":
    BDLASSDefender()
'''

os.makedirs(APPS, exist_ok=True)
with open(os.path.join(APPS, "virenschutz_app.py"), "w", encoding="utf-8") as f:
    f.write(virenschutz_code)

# 3. Icon
icon_base64 = (
    "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAxUlEQVRYhe2WsQ3CMAxF3xI"
    "kQBLkAEuQAS5ABKkQBLkAEuQATqVQnZ2dnbfZt2kqS7u7u7u7u7u7u7u7u7u7u7u7u7u7u"
    "7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u"
    "7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u"
    "7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u"
    "AAAAAElFTkSuQmCC"
)

os.makedirs(IMG, exist_ok=True)
with open(os.path.join(IMG, "defender_icon.png"), "wb") as f:
    f.write(base64.b64decode(icon_base64))

# 4. apps_info.json
apps_info = load_json(APPS_INFO, {})
apps_info["virenschutz_app.py"] = {
    "paths": [
        "apps/virenschutz_app.py",
        "apps/appdata/bdlass_defender",
        "images/defender_icon.png"
    ]
}
save_json(APPS_INFO, apps_info)

# 5. shortcuts.json
shortcuts = load_json(SHORTCUTS, [])
shortcuts.append({
    "name": "BDLASS Defender",
    "file": "virenschutz_app.py",
    "icon": "defender_icon.png"
})
save_json(SHORTCUTS, shortcuts)

# 6. apps_config.json
apps_cfg = load_json(APPS_CFG, [])
exists = any(a.get("file") == "virenschutz_app.py" for a in apps_cfg)
if not exists:
    apps_cfg.append({
        "name": "BDLASS Defender",
        "file": "virenschutz_app.py",
        "installer": "virenschutz_installer.py",
        "icon": "defender_icon.png",
        "description": "Standard-Schutz (B-Level) mit Upgrade auf Pro (C-Level).",
        "standard": False
    })
    save_json(APPS_CFG, apps_cfg)

print("BDLASS Defender erfolgreich installiert!")
