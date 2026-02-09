import subprocess

# ===== KONFIGURATION =====
# Der Name, den du deinem Epilog-Drucker im CUPS-System auf dem Pi gegeben hast
EPILOG_PRINTER_NAME = "epilog-raw" 
# =========================

def trigger_rework_laser(prn_file_path):
    """
    Sendet eine vordefinierte .prn-Datei als Druckjob an den Epilog-Laser,
    um einen Nacharbeits-Prozess zu starten.

    Args:
        prn_file_path (str): Der Pfad zur .prn-Datei für die Nachbearbeitung.

    Returns:
        bool: True, wenn der Befehl erfolgreich abgesetzt wurde, sonst False.
    """
    print(f"--- LASER-SCHNITTSTELLE: Starte Nacharbeits-Job ---")
    print(f"Drucker: {EPILOG_PRINTER_NAME}")
    print(f"Datei: {prn_file_path}")

    try:
        # Der Linux-Befehl, um einen Druckjob zu senden
        command = ["lp", "-d", EPILOG_PRINTER_NAME, prn_file_path]
        
        # Führe den Befehl aus. check=True sorgt dafür, dass bei einem Fehler
        # (z.B. Drucker nicht gefunden) eine Ausnahme ausgelöst wird.
        subprocess.run(command, check=True)
        
        print("✅ Nacharbeits-Job erfolgreich an den Laser gesendet.")
        return True

    except FileNotFoundError:
        # Dieser Fehler tritt auf, wenn der Befehl 'lp' nicht gefunden wird (sehr unwahrscheinlich)
        print("FEHLER: Der Druck-Befehl 'lp' wurde nicht gefunden. Ist CUPS installiert?")
        return False
    except subprocess.CalledProcessError as e:
        # Dieser Fehler tritt auf, wenn der 'lp'-Befehl einen Fehler zurückgibt
        # (z.B. der Druckername ist falsch oder der Drucker ist nicht erreichbar)
        print(f"FEHLER beim Senden des Druckjobs: {e}")
        return False
    except Exception as e:
        # Fängt alle anderen unerwarteten Fehler ab
        print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")
        return False