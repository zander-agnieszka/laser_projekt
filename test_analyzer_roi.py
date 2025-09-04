
import cv2
import numpy as np

# ===== KONFIGURATION (Diese Werte musst du anpassen!) =====

# --- NEU: GIB HIER DEINE GEMESSENEN ROI-KOORDINATEN EIN ---
ROI_Y_START = 1904   # Beispielwert: Obere Kante
ROI_Y_END = 2448   # Beispielwert: Untere Kante
ROI_X_START = 775  # Beispielwert: Linke Kante
ROI_X_END = 1465  # Beispielwert: Rechte Kante

# --- GEOMETRIE-PRÜFUNG ---
# Nimm die Werte, die du mit dem hsv_calibrator gefunden hast
LOWER_SILVER = np.array([0, 0, 127])
UPPER_SILVER = np.array([114, 103, 255])
# ... (Rest der Konfiguration bleibt erstmal gleich, passen wir später an) ...

# ====================================================================

test_image_path = "IO_Pictures/image_2025-08-12_11-04-51.jpg" # Passe den Pfad an

# --- Code-Beginn ---

image = cv2.imread(test_image_path)
if image is None:
    print(f"FEHLER: Bild konnte nicht geladen werden unter {test_image_path}")
    exit()

print(f"INFO: Dein Bild hat die Größe (Höhe, Breite): ({image.shape[0]}, {image.shape[1]})")    

# ===== SCHRITT 1: BILD AUF ROI ZUSCHNEIDEN =====
# Wir erstellen eine saubere Kopie des ROI für die Analyse
roi = image[ROI_Y_START:ROI_Y_END, ROI_X_START:ROI_X_END].copy()

# Wir erstellen eine weitere Kopie nur für die Anzeige, auf der wir malen können
output_roi = roi.copy()
hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

# ===== SCHRITT 2: ANALYSE NUR INNERHALB DES ROI =====
print("--- Starte Geometrie-Prüfung innerhalb des ROI ---")
silver_mask = cv2.inRange(hsv_roi, LOWER_SILVER, UPPER_SILVER)
contours, _ = cv2.findContours(silver_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

if not contours:
    print("-> Ergebnis: Kein silberner Cut-Out im ROI gefunden.")
else:
    cutout_contour = max(contours, key=cv2.contourArea)
    flaeche = cv2.contourArea(cutout_contour)
    M = cv2.moments(cutout_contour)
    cX = int(M["m10"] / M["m00"]) if M["m00"] != 0 else 0
    
    # Zeichne die gefundene Kontur auf unser ROI-Ausgabebild
    cv2.drawContours(output_roi, [cutout_contour], -1, (0, 255, 0), 2)
    print(f"-> Messung im ROI: Fläche={flaeche}, Position X={cX}")
    # ... hier würde dann die weitere Logik (if/else für IO/NIO etc.) folgen

# --- VISUALISIERUNG ---
# Zeige das Originalbild und daneben die Analyse-Fenster für den ROI
cv2.imshow("Ganzes Originalbild", image)
cv2.imshow("1 - ROI Ausschnitt", roi)
cv2.imshow("2 - Silber-Erkennung im ROI", silver_mask)
cv2.imshow("3 - Gefundene Kontur im ROI", output_roi)

cv2.waitKey(0)
cv2.destroyAllWindows()