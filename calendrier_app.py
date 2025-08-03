import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import calendar
import json
import requests

FICHIER_RES = "reservations.json"

# Palette de couleurs Leoni (bleu et orange foncé)
COULEURS = {
    "fond": "#0055A4",
    "header": "#FF5500",
    "cellule_vide": "#E6F0FA",
    "cellule_occupee": "#FFD8B3",
    "texte": "#003366",
    "bouton": "#FF5500",
    "bouton_texte": "white",
    "entete": "#003366",
    "selection": "#FF9966",
    "bouton_secondaire": "#0066CC"
}

def sauvegarder_reservations(data):
    with open(FICHIER_RES, "w") as f:
        json.dump(data, f, indent=4)

def charger_reservations():
    try:
        with open(FICHIER_RES, "r") as f:
            data = json.load(f)
            for k, v in data.items():
                if isinstance(v, dict):
                    data[k] = [v]
            return data
    except:
        return {}

class CalendrierApp:
    def __init__(self, root, parent=None, uid=None):
        self.root = root  # Utiliser la fenêtre passée (Toplevel) au lieu de créer une nouvelle Tk
        self.parent = parent  # Référence à l'interface RFID pour revenir après fermeture
        self.uid = uid  # UID de la carte scannée, si disponible
        self.root.title("Calendrier des Réservations - LEONI")
        self.root.configure(bg=COULEURS["fond"])
        self.root.state('zoomed')  # Plein écran

        # Configuration du style
        self.configurer_styles()

        self.reservations = charger_reservations()
        self.aujourdhui = datetime.today()
        self.mois = self.aujourdhui.month
        self.annee = self.aujourdhui.year

        self.creer_header()
        self.creer_calendrier()

    def configurer_styles(self):
        style = ttk.Style()
        style.theme_use('clam')

        style.configure('TButton',
                       background=COULEURS["bouton"],
                       foreground=COULEURS["bouton_texte"],
                       font=('Helvetica', 10, 'bold'),
                       borderwidth=1)
        style.map('TButton',
                 background=[('active', COULEURS["selection"])])

        style.configure('Secondary.TButton',
                       background=COULEURS["bouton_secondaire"],
                       foreground='white',
                       font=('Helvetica', 10, 'bold'))
        style.map('Secondary.TButton',
                 background=[('active', '#003366')])

        style.configure('Header.TLabel',
                       background=COULEURS["header"],
                       foreground='white',
                       font=('Helvetica', 14, 'bold'))

        style.configure('Month.TLabel',
                       background=COULEURS["fond"],
                       foreground='white',
                       font=('Helvetica', 16, 'bold'))

        style.configure('Jour.TLabel',
                       background=COULEURS["entete"],
                       foreground='white',
                       font=('Helvetica', 10, 'bold'))

    def creer_header(self):
        header = ttk.Frame(self.root, style='Header.TFrame')
        header.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(header, text="LEONI - Calendrier de Réservation", style='Header.TLabel').pack(side=tk.LEFT, padx=10)

        nav_frame = ttk.Frame(header)
        nav_frame.pack(side=tk.RIGHT, padx=10)

        ttk.Button(nav_frame, text="◀", width=3,
                  command=self.mois_precedent).pack(side=tk.LEFT, padx=2)
        ttk.Button(nav_frame, text="Aujourd'hui",
                  command=self.aller_aujourdhui).pack(side=tk.LEFT, padx=2)
        ttk.Button(nav_frame, text="▶", width=3,
                  command=self.mois_suivant).pack(side=tk.LEFT, padx=2)

    def mois_precedent(self):
        self.mois -= 1
        if self.mois == 0:
            self.mois = 12
            self.annee -= 1
        self.creer_calendrier()

    def mois_suivant(self):
        self.mois += 1
        if self.mois == 13:
            self.mois = 1
            self.annee += 1
        self.creer_calendrier()

    def aller_aujourdhui(self):
        self.mois = self.aujourdhui.month
        self.annee = self.aujourdhui.year
        self.creer_calendrier()

    def creer_calendrier(self):
        if hasattr(self, 'cal_frame'):
            self.cal_frame.destroy()

        self.cal_frame = ttk.Frame(self.root)
        self.cal_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        mois_nom = datetime(self.annee, self.mois, 1).strftime('%B %Y')
        header = ttk.Label(self.cal_frame, text=mois_nom, style='Month.TLabel')
        header.grid(row=0, column=0, columnspan=7, pady=(0, 10))

        jours = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
        for i, j in enumerate(jours):
            cell = ttk.Label(self.cal_frame, text=j, style='Jour.TLabel',
                            width=15, padding=5)
            cell.grid(row=1, column=i, padx=1, pady=1, sticky="nsew")

        cal = calendar.monthcalendar(self.annee, self.mois)
        for row, semaine in enumerate(cal):
            for col, jour in enumerate(semaine):
                if jour == 0:
                    continue

                date_str = f"{self.annee:04d}-{self.mois:02d}-{jour:02d}"
                cell_bg = COULEURS["cellule_occupee"] if date_str in self.reservations else COULEURS["cellule_vide"]

                cell_frame = tk.Frame(self.cal_frame, bg=cell_bg, bd=1,
                                     relief=tk.RAISED, highlightbackground="#cccccc")
                cell_frame.grid(row=row+2, column=col, padx=1, pady=1, sticky="nsew")

                jour_label = tk.Label(cell_frame, text=str(jour), bg=cell_bg,
                                     fg=COULEURS["texte"], anchor='nw',
                                     font=('Helvetica', 9, 'bold'))
                jour_label.pack(anchor='nw', padx=3, pady=2)

                btn = ttk.Button(cell_frame, text="Réserver",
                                command=lambda d=date_str: self.ouvrir_popup(d))
                btn.pack(side=tk.BOTTOM, fill=tk.X, padx=2, pady=2)

                if date_str in self.reservations:
                    res_frame = tk.Frame(cell_frame, bg=cell_bg)
                    res_frame.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)

                    for res in self.reservations[date_str][:2]:
                        info = f"{res['nom'][:8]}... {res['heure_debut']}-{res['heure_fin']}"
                        lbl = tk.Label(res_frame, text=info, bg=cell_bg,
                                      fg=COULEURS["texte"], font=('Helvetica', 8))
                        lbl.pack(anchor='w')

                    if len(self.reservations[date_str]) > 2:
                        more = tk.Label(res_frame, text=f"+{len(self.reservations[date_str])-2} de plus",
                                       bg=cell_bg, fg=COULEURS["texte"], font=('Helvetica', 7, 'italic'))
                        more.pack(anchor='w')

                    cell_frame.bind("<Button-1>", lambda e, d=date_str: self.afficher_details(d))
                    btn.bind("<Button-1>", lambda e, d=date_str: self.afficher_details(d))

        for i in range(7):
            self.cal_frame.columnconfigure(i, weight=1)
        for i in range(len(cal) + 2):
            self.cal_frame.rowconfigure(i, weight=1)

    def ouvrir_popup(self, date):
        popup = tk.Toplevel(self.root)
        popup.title(f"Réserver le {date}")
        popup.configure(bg=COULEURS["fond"])
        popup.geometry("400x500")
        self.centrer_fenetre(popup)
        popup.resizable(False, False)

        form_frame = tk.Frame(popup, bg=COULEURS["fond"], padx=20, pady=20)
        form_frame.pack(fill=tk.BOTH, expand=True)

        label_style = {'bg': COULEURS["fond"], 'fg': 'white', 'font': ('Helvetica', 10)}
        entry_style = {'font': ('Helvetica', 10), 'bd': 2, 'relief': tk.GROOVE, 'bg': 'white'}

        self.entries = {}
        champs = ["Nom", "Email", "Téléphone", "Objet"]

        for champ in champs:
            tk.Label(form_frame, text=champ, **label_style).pack(anchor='w', pady=(10, 0))
            entry = tk.Entry(form_frame, **entry_style)
            entry.pack(fill=tk.X, pady=5)
            self.entries[champ] = entry

        heures = [f"{h:02d}:{m:02d}" for h in range(8, 21) for m in (0, 30)]

        tk.Label(form_frame, text="Heure de début", **label_style).pack(anchor='w', pady=(10, 0))
        self.heure_debut = ttk.Combobox(form_frame, values=heures, state="readonly")
        self.heure_debut.pack(fill=tk.X, pady=5)
        self.heure_debut.current(0)

        tk.Label(form_frame, text="Heure de fin", **label_style).pack(anchor='w', pady=(10, 0))
        self.heure_fin = ttk.Combobox(form_frame, values=heures, state="readonly")
        self.heure_fin.pack(fill=tk.X, pady=5)
        self.heure_fin.current(1)

        btn_frame = tk.Frame(form_frame, bg=COULEURS["fond"])
        btn_frame.pack(fill=tk.X, pady=20)

        ttk.Button(btn_frame, text="Valider",
                  command=lambda: self.valider_reservation(date, popup)).pack(side=tk.RIGHT)

    def centrer_fenetre(self, fenetre):
        fenetre.update_idletasks()
        largeur = fenetre.winfo_width()
        hauteur = fenetre.winfo_height()
        x = (fenetre.winfo_screenwidth() // 2) - (largeur // 2)
        y = (fenetre.winfo_screenheight() // 2) - (hauteur // 2)
        fenetre.geometry(f"+{x}+{y}")

    def valider_reservation(self, date, popup):
        nom = self.entries["Nom"].get()
        email = self.entries["Email"].get()
        telephone = self.entries["Téléphone"].get()
        objet = self.entries["Objet"].get()
        debut = self.heure_debut.get()
        fin = self.heure_fin.get()

        format_heure = "%H:%M"
        try:
            heure_debut = datetime.strptime(debut, format_heure)
            heure_fin = datetime.strptime(fin, format_heure)
        except ValueError:
            messagebox.showerror("Erreur", "Format d'heure invalide. Utilisez HH:MM", parent=popup)
            return

        if not nom or not email or not objet:
            messagebox.showerror("Erreur", "Les champs Nom, Email et Objet sont obligatoires", parent=popup)
            return

        if heure_debut >= heure_fin:
            messagebox.showerror("Erreur", "L'heure de début doit être inférieure à l'heure de fin", parent=popup)
            return

        nouvelle_reservation = {
            "nom": nom,
            "email": email,
            "telephone": telephone,
            "objet": objet,
            "heure_debut": debut,
            "heure_fin": fin
        }

        if date not in self.reservations:
            self.reservations[date] = []

        for res in self.reservations[date]:
            res_debut = datetime.strptime(res["heure_debut"], format_heure)
            res_fin = datetime.strptime(res["heure_fin"], format_heure)
            if not (heure_fin <= res_debut or heure_debut >= res_fin):
                messagebox.showerror("Conflit", f"Conflit avec une autre réservation de {res['heure_debut']} à {res['heure_fin']}", parent=popup)
                return

        self.reservations[date].append(nouvelle_reservation)

        data = {
            "action": "add",
            "nom": nom,
            "email": email,
            "telephone": telephone,
            "objet": objet,
            "date_reservation": date,
            "heure_debut": debut,
            "heure_fin": fin
        }

        try:
            response = requests.post("http://localhost/reservation1/api_reservations.php", json=data)
            result = response.json()
            if result["status"] == "success":
                messagebox.showinfo("Succès", result["message"], parent=popup)
                popup.destroy()
                self.creer_calendrier()
                sauvegarder_reservations(self.reservations)
            else:
                messagebox.showerror("Erreur", result["message"], parent=popup)
        except Exception as e:
            messagebox.showerror("Erreur réseau", str(e), parent=popup)

    def afficher_details(self, date):
        if date not in self.reservations:
            return

        fen = tk.Toplevel(self.root)
        fen.title(f"Détails des réservations - {date}")
        fen.geometry("500x600")
        fen.configure(bg=COULEURS["fond"])
        self.centrer_fenetre(fen)

        tk.Label(fen, text=f"Réservations pour le {date}",
                font=("Helvetica", 14, "bold"),
                bg=COULEURS["fond"], fg="white", pady=10).pack()

        liste_frame = tk.Frame(fen, bg=COULEURS["fond"])
        liste_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        canvas = tk.Canvas(liste_frame, bg=COULEURS["fond"])
        scrollbar = ttk.Scrollbar(liste_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COULEURS["fond"])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for i, res in enumerate(self.reservations[date]):
            card = tk.Frame(scrollable_frame, bg="white", bd=1, relief=tk.RAISED)
            card.pack(fill=tk.X, padx=5, pady=5, ipadx=5, ipady=5)

            infos = f"• {res['heure_debut']} - {res['heure_fin']}\n"
            infos += f"• {res['nom']}\n"
            infos += f"• {res['objet']}\n"
            infos += f"• {res['email']} | {res['telephone']}"

            tk.Label(card, text=infos, font=("Helvetica", 10),
                    bg="white", anchor='w', justify=tk.LEFT).pack(padx=10, pady=5, fill=tk.X)

            btn_frame = tk.Frame(card, bg="white")
            btn_frame.pack(fill=tk.X, padx=10, pady=5)

            ttk.Button(btn_frame, text="Modifier", style='Secondary.TButton',
                      command=lambda r=res, d=date, idx=i: self.modifier_reservation(d, idx, r, fen)).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="Supprimer",
                      command=lambda d=date, idx=i, r=res: self.supprimer_reservation(d, idx, r, fen)).pack(side=tk.RIGHT, padx=5)

        ttk.Button(fen, text="+ Ajouter une réservation",
                  command=lambda: [self.ouvrir_popup(date), fen.destroy()]).pack(pady=10)

    def modifier_reservation(self, date, index, reservation, fenetre_parente):
        popup = tk.Toplevel(self.root)
        popup.title(f"Modifier la réservation du {date}")
        popup.configure(bg=COULEURS["fond"])
        popup.geometry("400x500")
        self.centrer_fenetre(popup)
        popup.resizable(False, False)

        form_frame = tk.Frame(popup, bg=COULEURS["fond"], padx=20, pady=20)
        form_frame.pack(fill=tk.BOTH, expand=True)

        label_style = {'bg': COULEURS["fond"], 'fg': 'white', 'font': ('Helvetica', 10)}
        entry_style = {'font': ('Helvetica', 10), 'bd': 2, 'relief': tk.GROOVE, 'bg': 'white'}

        self.entries_modif = {}
        champs = ["Nom", "Email", "Téléphone", "Objet"]

        for champ in champs:
            key = champ.lower().replace('é', 'e')
            tk.Label(form_frame, text=champ, **label_style).pack(anchor='w', pady=(10, 0))
            entry = tk.Entry(form_frame, **entry_style)
            entry.insert(0, reservation[key])
            if champ == "Email":
                entry.config(state='disabled')
            entry.pack(fill=tk.X, pady=5)
            self.entries_modif[champ] = entry

        heures = [f"{h:02d}:{m:02d}" for h in range(8, 21) for m in (0, 30)]

        tk.Label(form_frame, text="Heure de début", **label_style).pack(anchor='w', pady=(10, 0))
        self.heure_debut_modif = ttk.Combobox(form_frame, values=heures, state="readonly")
        self.heure_debut_modif.set(reservation["heure_debut"])
        self.heure_debut_modif.pack(fill=tk.X, pady=5)

        tk.Label(form_frame, text="Heure de fin", **label_style).pack(anchor='w', pady=(10, 0))
        self.heure_fin_modif = ttk.Combobox(form_frame, values=heures, state="readonly")
        self.heure_fin_modif.set(reservation["heure_fin"])
        self.heure_fin_modif.pack(fill=tk.X, pady=5)

        btn_frame = tk.Frame(form_frame, bg=COULEURS["fond"])
        btn_frame.pack(fill=tk.X, pady=20)

        ttk.Button(btn_frame, text="Annuler", style='Secondary.TButton',
                  command=popup.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Enregistrer",
                  command=lambda: self.valider_modification(date, index, popup, fenetre_parente)).pack(side=tk.RIGHT, padx=5)

    def valider_modification(self, date, index, popup, fenetre_parente):
        nom = self.entries_modif["Nom"].get()
        email = self.entries_modif["Email"].get()
        telephone = self.entries_modif["Téléphone"].get()
        objet = self.entries_modif["Objet"].get()
        debut = self.heure_debut_modif.get()
        fin = self.heure_fin_modif.get()

        format_heure = "%H:%M"
        try:
            heure_debut = datetime.strptime(debut, format_heure)
            heure_fin = datetime.strptime(fin, format_heure)
        except ValueError:
            messagebox.showerror("Erreur", "Format d'heure invalide. Utilisez HH:MM", parent=popup)
            return

        if not nom or not email or not objet:
            messagebox.showerror("Erreur", "Les champs Nom, Email et Objet sont obligatoires", parent=popup)
            return

        if heure_debut >= heure_fin:
            messagebox.showerror("Erreur", "L'heure de début doit être inférieure à l'heure de fin", parent=popup)
            return

        data = {
            "action": "edit",
            "nom": nom,
            "email": email,
            "telephone": telephone,
            "objet": objet,
            "date_reservation": date,
            "heure_debut": debut,
            "heure_fin": fin
        }

        try:
            response = requests.post("http://localhost/reservation1/api_reservations.php", json=data)
            result = response.json()
            if result["status"] == "success":
                self.reservations[date][index] = {
                    "nom": nom,
                    "email": email,
                    "telephone": telephone,
                    "objet": objet,
                    "heure_debut": debut,
                    "heure_fin": fin
                }
                popup.destroy()
                fenetre_parente.destroy()
                self.creer_calendrier()
                sauvegarder_reservations(self.reservations)
                messagebox.showinfo("Succès", "Réservation modifiée avec succès")
            else:
                messagebox.showerror("Erreur", result["message"], parent=popup)
        except Exception as e:
            messagebox.showerror("Erreur réseau", str(e), parent=popup)

    def supprimer_reservation(self, date, index, reservation, fenetre):
        if messagebox.askyesno("Confirmation", "Supprimer cette réservation ?", parent=fenetre):
            data = {
                "action": "delete",
                "email": reservation["email"],
                "date_reservation": date,
                "heure_debut": reservation["heure_debut"],
                "heure_fin": reservation["heure_fin"]
            }
            try:
                response = requests.post("http://localhost/reservation1/api_reservations.php", json=data)
                result = response.json()
                if result["status"] == "success":
                    del self.reservations[date][index]
                    if not self.reservations[date]:
                        del self.reservations[date]
                    sauvegarder_reservations(self.reservations)
                    fenetre.destroy()
                    self.creer_calendrier()
                else:
                    messagebox.showerror("Erreur", result["message"])
            except Exception as e:
                messagebox.showerror("Erreur réseau", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = CalendrierApp(root)
    root.mainloop()