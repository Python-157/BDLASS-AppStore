import os
import json
import base64

# Basis-Pfade
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPS = os.path.join(BASE, "apps")
IMG = os.path.join(BASE, "images")
APPDATA = os.path.join(APPS, "appdata", "kamera_app")
APPS_INFO = os.path.join(APPS, "apps_info.json")
SHORTCUTS = os.path.join(BASE, "shortcuts.json")

# ---------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------

def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.loads(f.read().strip() or "{}")
    except:
        return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ---------------------------------------------------
# 1. Kamera-App erstellen
# ---------------------------------------------------

kamera_app_code = r'''
import tkinter as tk
import cv2
from PIL import Image, ImageTk
import os
import time

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPDATA = os.path.join(BASE, "apps", "appdata", "kamera_app", "fotos")

class KameraApp:
    def __init__(self):
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

# App-Datei schreiben
os.makedirs(APPS, exist_ok=True)
with open(os.path.join(APPS, "kamera_app.py"), "w", encoding="utf-8") as f:
    f.write(kamera_app_code)

# ---------------------------------------------------
# 2. AppData Ordner erstellen
# ---------------------------------------------------

os.makedirs(os.path.join(APPDATA, "fotos"), exist_ok=True)

# ---------------------------------------------------
# 3. Icon aus Base64 erzeugen
# ---------------------------------------------------

# Beispiel-Icon (schwarzes 32x32 PNG)
icon_base64 = (
    "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAIElEQVR4nO3BMQEAAADCoPVPbQ0PoAAAAAAAAAAA"
    "AAAAAAAAAAAAAD4G4oAAWcZk90AAAAASUVORK5CYII="
)

icon_bytes = base64.b64decode(icon_base64)

os.makedirs(IMG, exist_ok=True)
with open(os.path.join(IMG, "kamera_icon.png"), "wb") as f:
    f.write(icon_bytes)

# ---------------------------------------------------
# 4. apps_info.json aktualisieren
# ---------------------------------------------------

apps_info = load_json(APPS_INFO, {})

apps_info["kamera_app.py"] = {
    "paths": [
        "apps/kamera_app.py",
        "apps/appdata/kamera_app",
        "images/kamera_icon.png"
    ]
}

save_json(APPS_INFO, apps_info)

# ---------------------------------------------------
# 5. Desktop-Shortcut hinzufügen
# ---------------------------------------------------

shortcuts = load_json(SHORTCUTS, [])
shortcuts.append({
    "name": "Kamera",
    "file": "kamera_app.py",
    "icon": "kamera_icon.png"
})
save_json(SHORTCUTS, shortcuts)

print("Kamera-App erfolgreich installiert!")
