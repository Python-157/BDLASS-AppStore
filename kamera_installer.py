import os
import json
import base64

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPS = os.path.join(BASE, "apps")
IMG = os.path.join(BASE, "images")
APPDATA = os.path.join(APPS, "appdata", "kamera_app")
APPS_INFO = os.path.join(APPS, "apps_info.json")
SHORTCUTS = os.path.join(BASE, "shortcuts.json")
APPS_CFG = os.path.join(APPS, "apps_config.json")

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

# 1. AppData
os.makedirs(os.path.join(APPDATA, "fotos"), exist_ok=True)

# 2. Kamera-App
kamera_code = r'''
import tkinter as tk
import cv2
from PIL import Image, ImageTk
import os
import time

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPDATA = os.path.join(BASE, "apps", "appdata", "kamera_app", "fotos")

class KameraApp:
    def __init__(self):
        os.makedirs(APPDATA, exist_ok=True)

        self.root = tk.Tk()
        self.root.title("Kamera")
        self.root.geometry("800x600")
        self.root.configure(bg="#202020")

        self.cap = cv2.VideoCapture(0)

        self.label = tk.Label(self.root, bg="#202020")
        self.label.pack(pady=10)

        tk.Button(self.root, text="📸 Foto machen",
                  command=self.take_photo,
                  bg="#404040", fg="white",
                  font=("Segoe UI", 12)).pack(pady=10)

        self.update_frame()
        self.root.mainloop()

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = ImageTk.PhotoImage(Image.fromarray(frame))
            self.label.config(image=img)
            self.label.image = img
        self.root.after(10, self.update_frame)

    def take_photo(self):
        ret, frame = self.cap.read()
        if ret:
            filename = os.path.join(APPDATA, f"foto_{int(time.time())}.png")
            cv2.imwrite(filename, frame)
            print("Foto gespeichert:", filename)

if __name__ == "__main__":
    KameraApp()
'''

os.makedirs(APPS, exist_ok=True)
with open(os.path.join(APPS, "kamera_app.py"), "w", encoding="utf-8") as f:
    f.write(kamera_code)

# 3. Icon (Dummy)
icon_base64 = (
    "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAIElEQVRYhe3BMQEAAADCoPVPbQhPoAAAAAAAAAAA"
    "AAAAAAAAAAAAAPgG4oABYtXK0QAAAABJRU5ErkJggg=="
)
os.makedirs(IMG, exist_ok=True)
with open(os.path.join(IMG, "kamera_icon.png"), "wb") as f:
    f.write(base64.b64decode(icon_base64))

# 4. apps_info.json
apps_info = load_json(APPS_INFO, {})
apps_info["kamera_app.py"] = {
    "paths": [
        "apps/kamera_app.py",
        "apps/appdata/kamera_app",
        "images/kamera_icon.png"
    ]
}
save_json(APPS_INFO, apps_info)

# 5. shortcuts.json
shortcuts = load_json(SHORTCUTS, [])
shortcuts.append({
    "name": "Kamera",
    "file": "kamera_app.py",
    "icon": "kamera_icon.png"
})
save_json(SHORTCUTS, shortcuts)

# 6. apps_config.json
apps_cfg = load_json(APPS_CFG, [])
exists = any(a.get("file") == "kamera_app.py" for a in apps_cfg)
if not exists:
    apps_cfg.append({
        "name": "Kamera",
        "file": "kamera_app.py",
        "installer": "kamera_installer.py",
        "icon": "kamera_icon.png",
        "description": "Macht Fotos und speichert sie als PNG.",
        "standard": False
    })
    save_json(APPS_CFG, apps_cfg)

print("Kamera-App erfolgreich installiert!")
