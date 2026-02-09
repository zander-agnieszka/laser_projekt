import cv2
import numpy as np

# ===== KONFIGURATION (Nur für Geometrie) =====
LOWER_SILVER = np.array([0, 0, 127])
UPPER_SILVER = np.array([114, 103, 255])

MIN_FLAECHE_CUTOUT = 63000
MAX_FLAECHE_CUTOUT = 77500

ERWARTETE_X_POS_ROI = 194
ERWARTETE_Y_POS_ROI = 126
POS_TOLERANZ = 15
# ===============================================

def check_geometry(hsv_roi):
    """
    Prüft die Geometrie (Größe und Position) des silbernen Cut-Outs im ROI.
    Gibt zurück: (True/False, Kontur, Mittelpunkt, Fläche, Maske)
    """
    silver_mask = cv2.inRange(hsv_roi, LOWER_SILVER, UPPER_SILVER)
    # Wir erstellen ein "Strukturelement" (einen kleinen Kasten), um damit zu arbeiten.
    # Die Größe (z.B. 5x5) steuert, wie "aggressiv" die Operation ist.
    # Größere Werte füllen größere Löcher.
    kernel = np.ones((5, 5), np.uint8)

    # Führe eine "Closing"-Operation durch. Das entfernt kleine schwarze Löcher in weißen Flächen.
    reparierte_maske = cv2.morphologyEx(silver_mask, cv2.MORPH_CLOSE, kernel)

    # Wir suchen die Konturen jetzt in der "reparierten" Maske!
    contours, _ = cv2.findContours(reparierte_maske, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        reason= "Kein Cut-Out gefunden"
        print(f"❌ Geometrie-Fehler: {reason}")
        return False, None, None, None, reason

    cutout_contour = max(contours, key=cv2.contourArea)
    flaeche = cv2.contourArea(cutout_contour)
    
    M = cv2.moments(cutout_contour)
    cX = int(M["m10"] / M["m00"]) if M["m00"] != 0 else 0
    cY = int(M["m01"] / M["m00"]) if M["m00"] != 0 else 0
    
    flaeche_ok = MIN_FLAECHE_CUTOUT < flaeche < MAX_FLAECHE_CUTOUT
    pos_ok = abs(cX - ERWARTETE_X_POS_ROI) <= POS_TOLERANZ and abs(cY - ERWARTETE_Y_POS_ROI) <= POS_TOLERANZ

    if not flaeche_ok:
        reason = f"Fläche ({flaeche}) außerhalb der Toleranz."
        print(f"❌ Geometrie-Fehler: {reason}")
        return False, cutout_contour, (cX, cY), flaeche, reason
        
    if not pos_ok:
        reason = f"Position (X:{cX}, Y:{cY}) außerhalb der Toleranz."
        print(f"❌ Geometrie-Fehler: {reason}")
        return False, cutout_contour, (cX, cY), flaeche, reason
    
    reason = f"Fläche: {int(flaeche)}, Position: ({cX}, {cY})"
    print(f"✅ Geometrie bestanden. (Fläche: {flaeche}, Position: (X:{cX}, Y:{cY}))")
    return True, cutout_contour, (cX, cY), flaeche, reason