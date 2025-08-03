import serial
import threading
import tkinter as tk
from tkinter import messagebox
import requests
from datetime import datetime

from calendrier_app import CalendrierApp  # Assure-toi que ce fichier existe

class RFIDInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Lecteur RFID")
        self.root.geometry("400x250")
        self.root.resizable(False, False)

        self.uid_var = tk.StringVar(value="En attente du scan...")
        self.status_var = tk.StringVar(value="🔴 Non connecté")
        self.stop_flag = threading.Event()
        self.card_uid = None  # UID de la carte scannée

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Lecteur RFID", font=("Segoe UI", 18)).pack(pady=10)

        tk.Label(self.root, text="Statut :", font=("Segoe UI", 12)).pack()
        tk.Label(self.root, textvariable=self.status_var, font=("Segoe UI", 12), fg="gray").pack()

        tk.Label(self.root, text="Dernier UID :", font=("Segoe UI", 12)).pack(pady=(15, 0))
        tk.Label(self.root, textvariable=self.uid_var, font=("Consolas", 16), fg="blue").pack()

        frame = tk.Frame(self.root)
        frame.pack(pady=20)

        tk.Button(frame, text="Démarrer", width=12, command=self.start_reading).grid(row=0, column=0, padx=10)
        tk.Button(frame, text="Arrêter", width=12, command=self.stop_reading).grid(row=0, column=1, padx=10)

    def start_reading(self):
        self.status_var.set("🟡 Connexion à COM4...")
        self.stop_flag.clear()
        threading.Thread(target=self.read_serial, daemon=True).start()

    def stop_reading(self):
        self.stop_flag.set()
        self.status_var.set("🔴 Lecture arrêtée")

    def check_card(self, card_uid):
        self.card_uid = card_uid
        try:
            response = requests.post(
                "http://localhost/reservation1/api_reservations.php",
                json={"action": "check_card", "card_uid": card_uid}
            )
            result = response.json()
            print("Réponse du backend :", result)

            if result["status"] == "success":
                if result["action"] == "show_calendar":
                    print("Tentative d'ouverture du calendrier...")
                    self.open_calendar()
                else:
                    print("Action non gérée :", result["action"])
            else:
                print("Carte non reconnue, accès refusé.")
        except Exception as e:
            print("Erreur réseau :", str(e))

    def open_calendar(self):
        try:
            print("Initialisation de la fenêtre du calendrier...")
            self.root.withdraw()
            calendrier_root = tk.Toplevel(self.root)
            calendrier_root.title("Calendrier des Réservations")
            self.calendrier_app = CalendrierApp(calendrier_root, parent=self, uid=self.card_uid)
            print("Calendrier créé avec succès")

            calendrier_root.protocol("WM_DELETE_WINDOW", lambda: self.on_calendar_close(calendrier_root))
        except Exception as e:
            print("Erreur dans open_calendar :", str(e))

    def on_calendar_close(self, calendrier_root):
        calendrier_root.destroy()
        self.root.deiconify()

    def read_serial(self):
        try:
            with serial.Serial("COM4", 9600, timeout=1) as ser:
                self.status_var.set("🟢 Connecté à COM4")
                while not self.stop_flag.is_set():
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if line and len(line) >= 4:
                        print("📟 UID reçu :", line)
                        self.uid_var.set(line)
                        self.check_card(line)
        except serial.SerialException as e:
            self.status_var.set(f"❌ COM4 inaccessible : {e}")
        except Exception as e:
            self.status_var.set(f"❌ Erreur : {e}")

    def on_close(self):
        self.stop_reading()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = RFIDInterface(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()()