# test_analyzer_roi.py (Version mit Gate 1 UND Gate 2)
import cv2
import numpy as np
import os

# ===== KONFIGURATION (Deine kalibrierten Werte!) =====
# --- ROI ---
ROI_Y_START = 1225 # Dein Wert
ROI_Y_END = 1500 # Dein Wert
ROI_X_START = 180 # Dein Wert
ROI_X_END = 650   # Dein Wert

# --- GEOMETRIE-PRÜFUNG ---
LOWER_SILVER = np.array([0, 0, 127]) # Dein kalibrierter Wert
UPPER_SILVER = np.array([114, 103, 255]) # Dein kalibrierter Wert

# Toleranzen für die Geometrie (Werte nach Kalibrierung eintragen)
MIN_FLAECHE_CUTOUT = 63000
MAX_FLAECHE_CUTOUT = 77500

#Toleranzen für die Position des Mittelpunkts (relativ zum ROI)
ERWARTETE_X_POS_ROI = 194 # Dein kalibrierter Wert
ERWARTETE_Y_POS_ROI = 126 # Dein kalibrierter Wert
POS_TOLERANZ = 30

# --- SAUBERKEITS-PRÜFUNG ---
# WICHTIG: Diese Werte mussen noch mal mit dem hsv_calibrator.py kalibrieret werden!
LOWER_BLUE = np.array([80, 37, 45])
UPPER_BLUE = np.array([130, 190, 153])
ANTEIL_BLAU_FUER_IO = 0.01 # Weniger als 1% blaue Pixel = I.O.

# ====================================================================

test_image_path = "Image/image_20250917_101430.jpg" # Ändere den Pfad!

# --- Code-Beginn  ---

image = cv2.imread(test_image_path)
# ... (ROI zuschneiden) ...
roi = image[ROI_Y_START:ROI_Y_END, ROI_X_START:ROI_X_END].copy()
output_roi = roi.copy()
hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)


# --- Geometrie-Prüfung (bleibt gleich) ---
silver_mask = cv2.inRange(hsv_roi, LOWER_SILVER, UPPER_SILVER)
contours, _ = cv2.findContours(silver_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

final_status = "nio"
final_mask_to_save = silver_mask # Standardmäßig die Silber-Maske speichern

if contours:
    cutout_contour = max(contours, key=cv2.contourArea)
    flaeche = cv2.contourArea(cutout_contour)
    M = cv2.moments(cutout_contour)
    cX = int(M["m10"] / M["m00"]) if M["m00"] != 0 else 0
    cY = int(M["m01"] / M["m00"]) if M["m00"] != 0 else 0
    
    flaeche_ok = MIN_FLAECHE_CUTOUT < flaeche < MAX_FLAECHE_CUTOUT
    pos_ok = abs(cX - ERWARTETE_X_POS_ROI) <= POS_TOLERANZ and abs(cY - ERWARTETE_Y_POS_ROI) <= POS_TOLERANZ

    if flaeche_ok and pos_ok:
        print("✅ Geometrie bestanden. Starte Gate 2: Sauberkeits-Prüfung...")
        
        # ===== HIER KOMMT DIE NEUE LOGIK FÜR GATE 2 =====
        cutout_mask = np.zeros_like(silver_mask)
        cv2.drawContours(cutout_mask, [cutout_contour], -1, 255, thickness=cv2.FILLED)
       
        
        blue_mask = cv2.inRange(hsv_roi, LOWER_BLUE, UPPER_BLUE)
        blaue_reste_maske = cv2.bitwise_and(blue_mask, blue_mask, mask=cutout_mask)
        
        blauer_anteil = np.sum(blaue_reste_maske > 0) / flaeche
        
        print(f"-> Messung Sauberkeit: Blauer Anteil = {blauer_anteil:.3%}")
        
        if blauer_anteil < ANTEIL_BLAU_FUER_IO:
            print("-> Ergebnis Sauberkeit: Cut-Out ist sauber.")
            final_status = "io"
        else:
            print("-> Ergebnis Sauberkeit: Blaue Reste gefunden.")
            final_status = "Blauanteil"
            
        final_mask_to_save = blaue_reste_maske # Wir wollen die blauen Reste im Ergebnisbild sehen
    else:
        print("❌ Geometrie-Prüfung fehlgeschlagen. STATUS: N.I.O.")
        # final_status bleibt 'nio'
else:
    print("❌ Geometrie-Prüfung fehlgeschlagen: Kein Cut-Out gefunden. STATUS: N.I.O.")
    # final_status bleibt 'nio'

# --- Finale Ausgabe und Speichern ---
print(f"\n--- ENDGÜLTIGER STATUS: {final_status.upper()} ---")

  # Zeichne die gefundene Kontur (grün) und den Mittelpunkt (rot)
cv2.drawContours(output_roi, [cutout_contour], -1, (0, 255, 0), 2)
cv2.circle(output_roi, (cX, cY), 7, (0, 0, 255), -1)

output_folder = "analyse_ergebnisse"
os.makedirs(output_folder, exist_ok=True)
cv2.imwrite(os.path.join(output_folder, f"ergebnis_{final_status}.jpg"), final_mask_to_save)
print(f"Ergebnisbild wurde in '{output_folder}' gespeichert.")

# --- NEUE VISUALISIERUNG: BILDER SPEICHERN ---
print("\n--- Speichere Analyse-Bilder ---")
output_folder = "analyse_ergebnisse"
os.makedirs(output_folder, exist_ok=True)

# Speichere die wichtigen Analyse-Schritte als Bilder
cv2.imwrite(os.path.join(output_folder, "1_roi_ausschnitt.jpg"), roi)
cv2.imwrite(os.path.join(output_folder, "2_silber_erkennung_maske.jpg"), silver_mask)
cv2.imwrite(os.path.join(output_folder, "3_gefundene_kontur_mit_mittelpunkt.jpg"),output_roi)


print(f"Ergebnisbilder wurden im Ordner '{output_folder}' gespeichert.")


cv2.waitKey(0)
cv2.destroyAllWindows()