import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import re
def get_wsl_distros():
    try:
        result = subprocess.run(["wsl", "--list", "--verbose"], capture_output=True)
        raw_output = result.stdout

        try:
            text = raw_output.decode("utf-16")
        except UnicodeDecodeError:
            text = raw_output.decode("utf-8", errors="ignore")

        lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
        if len(lines) <= 1:
            return []

        distros = []
        for line in lines[1:]:
            line = line.replace("*", "").strip()
            parts = re.split(r'\s{2,}', line)
            if len(parts) >= 3:
                name = parts[0].strip()
                state = parts[1].strip()
                version = parts[2].strip()
                distros.append((name, state, version))
        return distros

    except Exception as e:
        print("Fehler beim Abrufen der Distros:", e)
        return []



def start_distro(name):
    try:
        subprocess.Popen(["wsl", "-d", name])
    except Exception as e:
        messagebox.showerror("Fehler beim Start", str(e))

def remove_distro(name):
    confirm = messagebox.askyesno("Distro löschen", f"Soll '{name}' wirklich gelöscht werden?")
    if confirm:
        try:
            subprocess.run(["wsl", "--unregister", name], check=True)
            refresh()
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Fehler beim Löschen", e.stderr or str(e))
        except Exception as e:
            messagebox.showerror("Fehler beim Löschen", str(e))

def install_distro():
    distro = distro_var.get()
    if distro:
        try:
            subprocess.run(["wsl", "--install", "-d", distro], check=True)
            refresh()
        except Exception as e:
            messagebox.showerror("Fehler bei Installation", str(e))

def refresh():
    for widget in frame.winfo_children():
        widget.destroy()
    distros = get_wsl_distros()
    print(distros)
    if not distros:
        tk.Label(frame, text="Keine Distributionen gefunden.", fg="gray", bg="#1e1e1e").pack()
    for name, state, version in distros:
        row = tk.Frame(frame, bg="#1e1e1e")
        row.pack(fill="x", pady=5)

        tk.Label(row, text=name, width=20, anchor="w", fg="white", bg="#1e1e1e", font=("Segoe UI", 10)).pack(side="left", padx=5)
        tk.Label(row, text=f"({state}) (v{version})", fg="lightgray", bg="#1e1e1e").pack(side="left", padx=5)
        tk.Button(row, text="Starten", command=lambda n=name: start_distro(n), bg="#007acc", fg="white").pack(side="right", padx=2)
        tk.Button(row, text="Löschen", command=lambda n=name: remove_distro(n), bg="#cc0000", fg="white").pack(side="right", padx=2)

# GUI Setup
root = tk.Tk()
root.title("WSL GUI Launcher")
root.configure(bg="#1e1e1e")
root.geometry("480x400")

tk.Label(root, text="WSL Distributionen", fg="#ffcc66", bg="#1e1e1e", font=("Segoe UI", 16)).pack(pady=10)

frame = tk.Frame(root, bg="#1e1e1e")
frame.pack(fill="both", expand=True, padx=20)

refresh()

# Install section
install_frame = tk.Frame(root, bg="#1e1e1e")
install_frame.pack(fill="x", padx=20, pady=10)

distro_var = tk.StringVar()
available_distros = ["Ubuntu", "Debian", "Kali-Linux", "openSUSE-Leap-15.5"]
distro_dropdown = ttk.Combobox(install_frame, textvariable=distro_var, values=available_distros, state="readonly")
distro_dropdown.set("Distro auswählen")
distro_dropdown.pack(side="left", padx=5, fill="x", expand=True)

tk.Button(install_frame, text="Installieren", command=install_distro, bg="#28a745", fg="white").pack(side="left", padx=5)

root.mainloop()
