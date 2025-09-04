# test_analyzer.py
import cv2
import numpy as np

# ===== KONFIGURATION (Diese Werte musst du anpassen!) =====

# --- GEOMETRIE-PRÜFUNG ---
# WICHTIG: Die Erkennung von "Silber" ist schwierig und stark von der Beleuchtung abhängig.
# Wir definieren Silber als "wenig Farbe (Saturation) und hohe Helligkeit (Value)".
# Diese Werte MUSST du für dein Setup anpassen!
LOWER_SILVER = np.array([0, 0, 127])
UPPER_SILVER = np.array([114, 103, 255])

# Toleranzen für die Geometrie des Cut-Outs (in PIXEL)
# Diese Werte musst du nach der Kalibrierung ("Pixel pro Millimeter") eintragen.
MIN_FLAECHE_CUTOUT = 1800  # Beispielwert!
MAX_FLAECHE_CUTOUT = 2200  # Beispielwert!
ERWARTETE_X_POS = 25       # Beispielwert! Erwarteter Mittelpunkt auf der X-Achse
POS_TOLERANZ = 25           # +/- 25 Pixel Toleranz

# --- SAUBERKEITS-PRÜFUNG ---
# Diese Werte sind meist einfacher zu finden.
LOWER_BLUE = np.array([90, 60, 60])
UPPER_BLUE = np.array([130, 255, 255])
# Weniger als dieser Anteil an blauen Pixeln im Cut-Out gilt als sauber
ANTEIL_BLAU_FUER_IO = 0.005 # Entspricht 0.5%

# ====================================================================

# Wähle hier das Bild aus, das du testen möchtest
# Nimm zuerst ein Bild, bei dem die Geometrie falsch ist (N.I.O.)
# Dann eines, das Nachbearbeitung braucht.
# Zum Schluss eines, das perfekt ist (I.O.)
test_image_path = "IO_Pictures/image_2025-08-12_11-00-50.jpg" 
# test_image_path = "IO_Pictures/dein_io_testbild.jpg" 

# --- Code-Beginn ---

image = cv2.imread(test_image_path)
if image is None:
    print(f"FEHLER: Bild konnte nicht geladen werden unter {test_image_path}")
    exit()

# Wir erstellen eine Kopie, um darauf zu zeichnen, ohne das Original zu verändern
output_image = image.copy()
hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# ===== SCHRITT 1: GEOMETRIE-PRÜFUNG =====
print("--- Starte Gate 1: Geometrie-Prüfung ---")
silver_mask = cv2.inRange(hsv, LOWER_SILVER, UPPER_SILVER)
contours, _ = cv2.findContours(silver_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

final_status = "nio" # Standard-Annahme ist N.I.O.

if not contours:
    print("-> Ergebnis: Kein silberner Cut-Out gefunden. STATUS: N.I.O.")
else:
    cutout_contour = max(contours, key=cv2.contourArea)
    flaeche = cv2.contourArea(cutout_contour)
    
    # Zeichne die gefundene Kontur auf das Ausgabebild (in Grün)
    cv2.drawContours(output_image, [cutout_contour], -1, (0, 255, 0), 3)
    
    # Prüfe Fläche und Position
    M = cv2.moments(cutout_contour)
    cX = int(M["m10"] / M["m00"]) if M["m00"] != 0 else 0
    
    print(f"-> Messung: Fläche={flaeche}, Position X={cX}")
    
    if not (MIN_FLAECHE_CUTOUT < flaeche < MAX_FLAECHE_CUTOUT):
        print(f"-> Ergebnis: Fläche ({flaeche}) außerhalb der Toleranz. STATUS: N.I.O.")
        final_status = "nio"
    elif abs(cX - ERWARTETE_X_POS) > POS_TOLERANZ:
        print(f"-> Ergebnis: Position ({cX}) außerhalb der Toleranz. STATUS: N.I.O.")
        final_status = "nio"
    else:
        print("✅ Geometrie bestanden. Starte Gate 2: Sauberkeits-Prüfung...")
        
        # ===== SCHRITT 2: SAUBERKEITS-PRÜFUNG =====
        cutout_mask = np.zeros_like(silver_mask)
        cv2.drawContours(cutout_mask, [cutout_contour], -1, 255, thickness=cv2.FILLED)
        
        blue_mask = cv2.inRange(hsv, LOWER_BLUE, UPPER_BLUE)
        blaue_reste_maske = cv2.bitwise_and(blue_mask, blue_mask, mask=cutout_mask)
        
        blauer_anteil = np.sum(blaue_reste_maske > 0) / flaeche
        
        print(f"-> Messung: Blauer Anteil im Cut-Out = {blauer_anteil:.3%}")
        
        if blauer_anteil < ANTEIL_BLAU_FUER_IO:
            print("-> Ergebnis: Cut-Out ist sauber. STATUS: I.O.")
            final_status = "io"
        else:
            print("-> Ergebnis: Blaue Reste gefunden. STATUS: NACHBEARBEITUNG.")
            final_status = "nachbearbeitung"

# --- VISUALISIERUNG ---
print(f"\n--- ENDGÜLTIGER STATUS: {final_status.upper()} ---")

# Zeige die Masken an, um zu sehen, was der Computer erkennt
cv2.imshow("1 - Silber-Erkennung (fuer Geometrie)", silver_mask)
cv2.imshow("2 - Original mit gefundener Kontur", output_image)

cv2.waitKey(0)
cv2.destroyAllWindows()