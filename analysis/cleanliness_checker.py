import cv2
import numpy as np

# ===== KONFIGURATION (Nur für Sauberkeit) =====
ANTEIL_NICHT_SILBER = 0.001 # 0,1% blaue Reste erlauben
# =============================================

    
def check_cleanliness(hsv_roi, valid_cutout_contour, silver_mask): # die silver_mask wird übertagen
    """
    Prüft die Sauberkeit durch inverse Maskierung.
    Sucht nach allen Pixeln im Cut-Out, die NICHT als "Silber" definiert sind.
    Gibt zurück: ('io' oder 'nachbearbeitung', Maske der unsauberen Reste)
    """
    # 1. Erstelle eine Maske nur für den Bereich des korrekten Cut-Outs
    cutout_mask = np.zeros_like(hsv_roi[:, :, 0])
    cv2.drawContours(cutout_mask, [valid_cutout_contour], -1, 255, thickness=cv2.FILLED)

    # 2. Finde die "guten" (sauberen) Pixel, die INNERHALB des Cut-Outs liegen
    saubere_pixel_maske = cv2.bitwise_and(silver_mask, silver_mask, mask=cutout_mask)

    # 3. Finde die "schlechten" (unsauberen) Pixel durch logische Subtraktion (XOR)
    # unsauber = (Gesamter Cut-Out) OHNE (die sauberen Pixel darin)
    unsaubere_reste_maske = cv2.bitwise_xor(cutout_mask, saubere_pixel_maske)

    # 4. Berechne den Anteil der unsauberen Reste
    unsaubere_pixel_im_cutout = np.sum(unsaubere_reste_maske > 0)
    flaeche_cutout = cv2.contourArea(valid_cutout_contour)
    unsauberer_anteil = ((unsaubere_pixel_im_cutout / flaeche_cutout)*100) if flaeche_cutout > 0 else 0

    print(f"Sauberkeits-Prüfung: Anteil unsauberer Pixel = {unsauberer_anteil:.2%}")

    if unsauberer_anteil < ANTEIL_NICHT_SILBER: 
        print("-> Ergebnis: Cut-Out ist sauber.")
        return "io", unsaubere_reste_maske
    else:
        print("-> Ergebnis: Reste gefunden (nicht-silber).")
        return "nachbearbeitung", unsaubere_reste_maske

