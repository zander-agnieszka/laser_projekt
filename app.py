from flask import Flask, render_template, redirect
import os

# Importiere deine "Experten"-Module
from camera_handler import capture_image_after_cleaning
from main_analyzer import run_full_analysis

# --- Flask App Initialisierung und Konfiguration der Pfade ---
app = Flask(__name__)

IMAGE_CAPTURE_FOLDER = "uploads"
ANALYSIS_OUTPUT_FOLDER = os.path.join('static', 'analyse_ergebnisse')

# --- Flask-Routen: Die Logik für die Webseite ---
@app.route("/")
def index():
    """Zeigt die Startseite an."""
    return render_template('index.html')

@app.route("/start_analysis")
def start_analysis():
    """Wird durch Klick auf den Button ausgelöst: Kamera -> Analyse -> Ergebnisseite."""
    print("--- ANFORDERUNG VOM WEB-INTERFACE: Starte Analyseprozess ---")
    
    # Schritt 1: Kamera-Experten aufrufen
    captured_image_path = capture_image_after_cleaning(folder_path=IMAGE_CAPTURE_FOLDER)
    if captured_image_path is None:
        return "<h1>FEHLER: Konnte kein Bild von der Kamera aufnehmen.</h1><a href='/'>Zurück</a>"

    # Schritt 2: Analyse-Experten aufrufen
    final_status, result_images = run_full_analysis(captured_image_path, output_folder=ANALYSIS_OUTPUT_FOLDER)
    if final_status is None:
        return "<h1>FEHLER: Die Bildanalyse ist fehlgeschlagen.</h1><a href='/'>Zurück</a>"
        
    print(f"--- ANALYSE ABGESCHLOSSEN: Status ist {final_status.upper()} ---")

    # Schritt 3: Ergebnisseite mit den Daten der Experten rendern
    return render_template('result.html', status=final_status, images=result_images)

# --- Startpunkt: Den Webserver starten ---
if __name__ == "__main__":
    os.makedirs(IMAGE_CAPTURE_FOLDER, exist_ok=True)
    os.makedirs(ANALYSIS_OUTPUT_FOLDER, exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)