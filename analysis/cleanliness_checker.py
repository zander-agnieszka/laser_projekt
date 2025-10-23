import cv2
import numpy as np

# ===== KONFIGURATION (Nur für Sauberkeit) =====
LOWER_SILVER = np.array([0, 0, 127])
UPPER_SILVER = np.array([114, 103, 255])

ANTEIL_NICHT_SILBER = 0.001 # 0,1% blaue Reste erlauben
# =============================================

    
def check_cleanliness(hsv_roi, valid_cutout_contour, flaeche_cutout):
    """
    Prüft die Sauberkeit durch inverse Maskierung.
    Sucht nach allen Pixeln im Cut-Out, die NICHT als "Silber" definiert sind.
    Gibt zurück: ('io' oder 'nachbearbeitung', Maske der unsauberen Reste)
    """
    # 1. Erstelle eine Maske nur für den Bereich des korrekten Cut-Outs.
    # Diese hat garantiert die richtige Größe.
    cutout_mask = np.zeros_like(hsv_roi[:, :, 0])
    cv2.drawContours(cutout_mask, [valid_cutout_contour], -1, 255, thickness=cv2.FILLED)

    # 2. Finde ALLE sauberen "Silber"-Pixel im gesamten ROI.
    silver_mask_im_roi = cv2.inRange(hsv_roi, LOWER_SILVER, UPPER_SILVER)

    # 3. Finde die sauberen Pixel, die INNERHALB des validierten Cut-Outs liegen.
    saubere_pixel_im_cutout_mask = cv2.bitwise_and(silver_mask_im_roi, silver_mask_im_roi, mask=cutout_mask)

    # 4. Finde die "schlechten" Pixel durch logische Subtraktion (XOR).
    unsaubere_reste_maske = cv2.bitwise_xor(cutout_mask, saubere_pixel_im_cutout_mask)

    # 5. Berechne den Anteil der unsauberen Reste.
    unsaubere_pixel_im_cutout = np.sum(unsaubere_reste_maske > 0)
    unsauberer_anteil = ((unsaubere_pixel_im_cutout / flaeche_cutout)*100) if flaeche_cutout > 0 else 0

    print(f"-> Messung Sauberkeit: Anteil unsauberer Pixel = {unsauberer_anteil:.3%}")

    if unsauberer_anteil < ANTEIL_NICHT_SILBER:
        print("-> Ergebnis Sauberkeit: Cut-Out ist sauber.")
        return "io", unsaubere_reste_maske
    else:
        print("-> Ergebnis Sauberkeit: Reste gefunden (nicht-silber).")
        return "nachbearbeitung", unsaubere_reste_maske

