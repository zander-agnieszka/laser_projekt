import os
import time
from datetime import datetime
from picamera2 import Picamera2

# ===== KONFIGURATION =====
# Standard-Speicherort für die Bilder
DEFAULT_IMAGE_FOLDER = "Image" 
# =========================


def capture_image_after_cleaning(folder_path=DEFAULT_IMAGE_FOLDER, filename_prefix="image"):
    """
    Initialisiert die Kamera, nimmt ein Bild auf und speichert es mit einem
    Zeitstempel im angegebenen Ordner.

    Args:
        folder_path (str): Der Ordner, in dem das Bild gespeichert werden soll.
        filename_prefix (str): Ein Präfix für den Dateinamen (z.B. 'vorher', 'nachher').

    Returns:
        str: Der vollständige Dateipfad zum gespeicherten Bild oder None bei einem Fehler.
    """
    try:
        # --- Verbesserung 1: Kamera-Initialisierung gekapselt ---
        # Die Kamera wird nur bei Bedarf initialisiert und nicht global.
        print("Initialisiere Kamera...")
        picam2 = Picamera2()
        
        # --- Verbesserung 2: Robuste Konfiguration ---
        # Wir erstellen eine Konfiguration und wenden sie an. Das ist stabiler.
        config = picam2.create_still_configuration()
        picam2.configure(config)

        # --- Verbesserung 3: Ordner erstellen, falls er nicht existiert ---
        # Das verhindert Fehler, wenn der Ordner versehentlich gelöscht wurde.
        os.makedirs(folder_path, exist_ok=True)

        print("Starte Kamera...")
        picam2.start()
        # Eine kurze Wartezeit gibt der Kamera Zeit, Belichtung und Fokus anzupassen (Auto-Exposure/Focus).
        time.sleep(2)

        # --- Verbesserung 4: Flexibler und eindeutiger Dateiname ---
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.jpg"
        full_path = os.path.join(folder_path, filename)
        
        print(f"Nehme Bild auf und speichere es als {full_path}...")
        picam2.capture_file(full_path)
        
        print("Bildaufnahme erfolgreich.")
        return full_path

    except Exception as e:
        # --- Verbesserung 5: Fehlerbehandlung ---
        # Wenn etwas schiefgeht (z.B. Kamera nicht angeschlossen), stürzt das Programm
        # nicht ab, sondern gibt eine Fehlermeldung und 'None' zurück.
        print(f"FEHLER bei der Bildaufnahme: {e}")
        return None
        
    finally:
        # --- Verbesserung 6: Sauberes Beenden der Kamera ---
        # Stellt sicher, dass die Kamera immer gestoppt wird, um Ressourcen freizugeben.
        if 'picam2' in locals() and picam2.started:
            picam2.stop()
            print("Kamera gestoppt.")
            picam2.close() # Diese Zeile ist neu und wichtig!
            print("Kamera-Ressource geschlossen.")


# ===== Beispiel zur Verwendung der Funktion =====
if __name__ == "__main__":
    # Dieser Teil wird nur ausgeführt, wenn du das Skript direkt startest (z.B. zum Testen)
    
    print("--- Test der Bildaufnahme ---")
    
    # Beispiel 1: Standard-Aufnahme
    gespeicherter_pfad = capture_image_after_cleaning()
    if gespeicherter_pfad:
        print(f"Test 1 erfolgreich! Bild liegt in: {gespeicherter_pfad}")
    else:
        print("Test 1 fehlgeschlagen.")

    print("\n--- Nächster Test in 5 Sekunden ---")
    time.sleep(5)

    # Beispiel 2: Aufnahme mit anderem Präfix in einem anderen Ordner
    gespeicherter_pfad_2 = capture_image_after_cleaning(folder_path="Nachher_Bilder_test", filename_prefix="nach_der_reinigung")
    if gespeicherter_pfad_2:
        print(f"Test 2 erfolgreich! Bild liegt in: {gespeicherter_pfad_2}")
    else:
        print("Test 2 fehlgeschlagen.")