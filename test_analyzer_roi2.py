# test_analyzer_roi.py (Version mit Flächen- UND Positionsprüfung)
import cv2
import numpy as np
import os

# ===== KONFIGURATION (Diese Werte musst du anpassen!) =====

# --- ROI (Region of Interest) ---
ROI_Y_START = 1225
ROI_Y_END = 1475
ROI_X_START = 270
ROI_X_END = 650

# --- GEOMETRIE-PRÜFUNG ---
# Deine kalibrierten Werte aus dem hsv_calibrator.py
LOWER_SILVER = np.array([0, 0, 127])
UPPER_SILVER = np.array([114, 103, 255])

# Toleranzen für die Geometrie (Werte nach Kalibrierung eintragen)
MIN_FLAECHE_CUTOUT = 63000  # Dein berechneter Mindestwert
MAX_FLAECHE_CUTOUT = 77500  # Dein berechneter Maximalwert

# NEU: Toleranzen für die Position des Mittelpunkts (relativ zum ROI)
ERWARTETE_X_POS_ROI = 194  # Beispiel: Mittelpunkt sollte bei X=150 IM ROI liegen
ERWARTETE_Y_POS_ROI = 126     # Beispiel: Mittelpunkt sollte bei Y=50 IM ROI liegen
POS_TOLERANZ = 25           # +/- 25 Pixel Toleranz in X- und Y-Richtung

# ... (Rest der Konfiguration für Sauberkeit bleibt gleich) ...

# ====================================================================

test_image_path = "Image/image_20250918_100923.jpg" # Passe den Pfad an

# --- Code-Beginn ---

image = cv2.imread(test_image_path)
if image is None:
    print(f"FEHLER: Bild konnte nicht geladen werden unter {test_image_path}")
    exit()

# Bild auf ROI zuschneiden
roi = image[ROI_Y_START:ROI_Y_END, ROI_X_START:ROI_X_END].copy()
if roi.size == 0:
    print(f"FEHLER: ROI ist leer. Überprüfe die ROI-Koordinaten!")
    exit()

output_roi = roi.copy()
hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

print("--- Starte Geometrie-Prüfung innerhalb des ROI ---")
silver_mask = cv2.inRange(hsv_roi, LOWER_SILVER, UPPER_SILVER)
contours, _ = cv2.findContours(silver_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

if not contours:
    print("-> Ergebnis: Kein silberner Cut-Out im ROI gefunden.")
else:
    cutout_contour = max(contours, key=cv2.contourArea)
    flaeche = cv2.contourArea(cutout_contour)
    
    # --- NEU: BERECHNUNG DES MITTELPUNKTS ---
    M = cv2.moments(cutout_contour)
    # Berechne den Mittelpunkt (cX, cY) der Kontur
    cX = int(M["m10"] / M["m00"]) if M["m00"] != 0 else 0
    cY = int(M["m01"] / M["m00"]) if M["m00"] != 0 else 0
    
    # Zeichne die gefundene Kontur (grün) und den Mittelpunkt (rot)
    cv2.drawContours(output_roi, [cutout_contour], -1, (0, 255, 0), 2)
    cv2.circle(output_roi, (cX, cY), 7, (0, 0, 255), -1)
    
    print(f"-> Messung im ROI: Fläche={flaeche}, Mittelpunkt=(X:{cX}, Y:{cY})")
    
    # --- NEU: PRÜFUNG VON FLÄCHE UND POSITION ---
    flaeche_ok = MIN_FLAECHE_CUTOUT < flaeche < MAX_FLAECHE_CUTOUT
    x_pos_ok = abs(cX - ERWARTETE_X_POS_ROI) <= POS_TOLERANZ
    y_pos_ok = abs(cY - ERWARTETE_Y_POS_ROI) <= POS_TOLERANZ
    
    if not flaeche_ok:
        print(f"-> Ergebnis: Fläche ({flaeche}) ist außerhalb der Toleranz. STATUS: N.I.O.")
    elif not x_pos_ok or not y_pos_ok:
        print(f"-> Ergebnis: Position (X:{cX}, Y:{cY}) ist außerhalb der Toleranz. STATUS: N.I.O.")
    else:
        print("✅ Geometrie bestanden.")
        # ... hier würde dann die Sauberkeitsprüfung folgen ...

# --- VISUALISIERUNG ---
# ... (Speichern oder Anzeigen der Bilder) ...
output_folder = "analyse_ergebnisse"
os.makedirs(output_folder, exist_ok=True)
cv2.imwrite(os.path.join(output_folder, "3_gefundene_kontur_mit_mittelpunkt.jpg"), output_roi)
print(f"Analysebild wurde in '{output_folder}' gespeichert.")