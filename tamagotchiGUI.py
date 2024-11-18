# Tamagotchi Spiel mit GUI
# Datum: 2024.08.05

import tkinter as tk
from tkinter import messagebox, simpledialog
import time
import threading
import json
import os
from datetime import datetime, timedelta

class Tamagotchi:
    def __init__(self, name, age, species, description, energy, hunger, mood, abilities, created_at, fat_obesity):
        self.name = name
        self.age = age
        self.species = species
        self.description = description
        self.energy = energy
        self.hunger = hunger
        self.mood = mood
        self.abilities = abilities
        self.alive = energy > 0 and (datetime.now() - datetime.fromisoformat(created_at)) < timedelta(days=365)
        self.overfed_days = 0
        self.created_at = datetime.fromisoformat(created_at)
        self.max_lifespan = timedelta(days=365)  # 1 Jahr
        self.fat_obesity = fat_obesity

    def __str__(self):
        status = (f"Name: {self.name}\n"
                  f"Alter: {self.age} Tage\n"
                  f"Spezies: {self.species}\n"
                  f"Beschreibung: {self.description}\n"
                  f"Energie: {self.energy}/100\n"
                  f"Hunger: {self.hunger}/100\n"
                  f"Laune: {self.mood}/100\n"
                  f"Fähigkeiten: {', '.join(self.abilities)}\n"
                  f"Verbleibende Lebensdauer: {self.remaining_life_days()} Tage\n")
        if self.fat_obesity:
            status += "Status: Fettleibig\n"
        return status

    def to_dict(self):
        return {
            "name": self.name,
            "age": self.age,
            "species": self.species,
            "description": self.description,
            "energy": self.energy,
            "hunger": self.hunger,
            "mood": self.mood,
            "abilities": self.abilities,
            "alive": self.alive,
            "created_at": self.created_at.isoformat(),
            "fat_obesity": self.fat_obesity
        }

    def remaining_life_days(self):
        return (self.max_lifespan - (datetime.now() - self.created_at)).days

    def update_energy(self):
        self.energy -= 1
        if self.energy <= 0:
            self.alive = False
            self.energy = 0
        if self.hunger > 100:
            self.overfed_days += 1
        if self.overfed_days >= 30:
            self.alive = False

    def feed(self):
        self.hunger += 20
        if self.hunger > 100:
            self.hunger = 100
        self.check_obesity()

    def pet(self):
        self.mood += 10
        if self.mood > 100:
            self.mood = 100

    def check_obesity(self):
        if self.hunger > 80:
            self.fat_obesity = True

def save_character(character, filename="characters.json"):
    data = []
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            data = json.load(file)

    # Entferne ggf. einen alten Eintrag mit demselben Namen
    data = [char for char in data if char["name"] != character.name]
    data.append(character.to_dict())
    
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

def load_characters(filename="characters.json"):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            data = json.load(file)
        return [Tamagotchi(**char) for char in data]
    return []

def character_lifecycle(character, update_interval=1):
    while character.alive and character.remaining_life_days() > 0:
        time.sleep(update_interval * 60)  # Aktualisierung jede Minute
        character.update_energy()
        if not character.alive:
            save_character(character)
            update_status()
            messagebox.showinfo("Charakter gestorben", f"{character.name} ist gestorben.")
            break
        update_status()

def update_status():
    if current_character:
        status_text = (f"Name: {current_character.name}\n"
                       f"Alter: {current_character.age} Tage\n"
                       f"Spezies: {current_character.species}\n"
                       f"Beschreibung: {current_character.description}\n"
                       f"Energie: {current_character.energy}/100\n"
                       f"Hunger: {current_character.hunger}/100\n"
                       f"Laune: {current_character.mood}/100\n"
                       f"Fettleibigkeit: {'Ja' if current_character.fat_obesity else 'Nein'}\n"
                       f"Verbleibende Lebensdauer: {current_character.remaining_life_days()} Tage\n")
        status_label.config(text=status_text)

# Funktion zur Auswahl des Charakters
def select_character():
    choice = character_var.get()
    if choice == 1:
        selected_species.set("Hase")
        selected_description.set("Hoppy ist ein freundlicher und energiegeladener Hase. Er liebt es zu springen und frische Karotten zu essen.")
        selected_abilities.set("Springen, Buddeln, Karotten suchen")
        selected_energy.set(100)
        selected_hunger.set(0)
        selected_mood.set(100)
    elif choice == 2:
        selected_species.set("Katze")
        selected_description.set("Luna ist eine elegante und mysteriöse Katze. Sie liebt es, im Sonnenschein zu faulenzen und mit Spielzeugmäusen zu spielen.")
        selected_abilities.set("Klettern, Schleichen, Mäuse fangen")
        selected_energy.set(100)
        selected_hunger.set(0)
        selected_mood.set(100)
    else:
        messagebox.showerror("Fehler", "Ungültige Auswahl.")
        return

    # Name-Eingabefeld aktivieren
    name_entry.config(state='normal')

# Funktion zur Erstellung des Charakters
def create_character():
    global current_character
    selected_name = name_var.get()
    if not selected_name:
        messagebox.showerror("Fehler", "Bitte geben Sie einen Namen ein.")
        return

    current_character = Tamagotchi(
        name=selected_name,
        age=1,  # Alter von 1 Tag
        species=selected_species.get(),
        description=selected_description.get(),
        energy=selected_energy.get(),
        hunger=selected_hunger.get(),
        mood=selected_mood.get(),
        abilities=selected_abilities.get().split(", "),
        created_at=datetime.now().isoformat(),
        fat_obesity=False
    )

    save_character(current_character)
    threading.Thread(target=character_lifecycle, args=(current_character,), daemon=True).start()
    update_status()

# Funktionen für Füttern und Streicheln
def feed_character():
    if current_character and current_character.alive:
        current_character.feed()
        update_status()

def pet_character():
    if current_character and current_character.alive:
        current_character.pet()
        update_status()

# Funktion zum Laden der Charaktere
def load_characters_ui():
    characters = load_characters()
    if characters:
        char_names = [char.name for char in characters]
        selected_char = simpledialog.askstring("Gespeicherte Charaktere", "Verfügbare Charaktere: \n" + "\n".join(char_names) + "\n\nGeben Sie den Namen des Charakters ein, den Sie laden möchten:")
        if selected_char:
            global current_character
            current_character = next((char for char in characters if char.name == selected_char), None)
            if current_character:
                threading.Thread(target=character_lifecycle, args=(current_character,), daemon=True).start()
                update_status()
            else:
                messagebox.showerror("Fehler", f"Charakter mit dem Namen '{selected_char}' nicht gefunden.")
    else:
        messagebox.showinfo("Gespeicherte Charaktere", "Keine gespeicherten Charaktere gefunden.")

def save_current_character():
    if current_character:
        save_character(current_character)
        messagebox.showinfo("Gespeichert", f"Charakter {current_character.name} wurde gespeichert.")
    else:
        messagebox.showwarning("Speichern fehlgeschlagen", "Kein Charakter ausgewählt.")

# Hauptfenster erstellen
root = tk.Tk()
root.title("Tamagotchi Auswahl")

# GUI-Elemente
character_var = tk.IntVar()
selected_species = tk.StringVar()
selected_description = tk.StringVar()
selected_abilities = tk.StringVar()
selected_energy = tk.IntVar()
selected_hunger = tk.IntVar()
selected_mood = tk.IntVar()
name_var = tk.StringVar()
current_character = None

tk.Label(root, text="Wählen Sie Ihren Charakter:").pack()
tk.Radiobutton(root, text="Hase", variable=character_var, value=1).pack(anchor=tk.W)
tk.Radiobutton(root, text="Katze", variable=character_var, value=2).pack(anchor=tk.W)
tk.Button(root, text="Auswählen", command=select_character).pack()

tk.Label(root, text="Geben Sie den Namen für den ausgewählten Charakter ein:").pack()
name_entry = tk.Entry(root, textvariable=name_var, state='disabled')
name_entry.pack()

tk.Button(root, text="Charakter erstellen", command=create_character).pack()
tk.Button(root, text="Füttern", command=feed_character).pack()
tk.Button(root, text="Streicheln", command=pet_character).pack()
tk.Button(root, text="Charaktere laden", command=load_characters_ui).pack()
tk.Button(root, text="Charakter speichern", command=save_current_character).pack()

# Status-Anzeige
status_label = tk.Label(root, text="Status: Kein Charakter ausgewählt.")
status_label.pack()

# Hauptschleife
root.mainloop()


