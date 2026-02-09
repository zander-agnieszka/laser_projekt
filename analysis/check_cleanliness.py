import cv2
import numpy as np
from analysis.geometry_checker import LOWER_SILVER, UPPER_SILVER

# ===== NEUE KONFIGURATION FÜR SAUBERKEITS-FILTER =====
# Farbwerte für "Blau/Grau" - Definiere, was ein "echter" Defekt ist.
LOWER_DEFECT_COLOR = np.array([40, 20, 20])
UPPER_DEFECT_COLOR = np.array([155, 255, 180])

# Mindestgröße in Pixeln, die ein Defekt haben muss, um nicht als Rauschen ignoriert zu werden.
MIN_DEFEKT_FLAECHE = 1


# Der Grenzwert für die Gesamt-Defektfläche
ANTEIL_DEFEKT_FUER_NACHARBEIT = 0.00001 # 0.001%
# =========================================================

def check_cleanliness(hsv_roi, bgr_roi, valid_cutout_contour, flaeche_cutout):
    """
    Prüft die Sauberkeit mit einem intelligenten Filter.
    Unterscheidet zwischen echten Defekten (blau/grau) und Störungen (Kratzer).
    Gibt zurück: ('io' oder 'nachbearbeitung', Maske der ECHTEN Defekte, Anteil)
    """
    # 1. Maske für den gesamten Cut-Out-Bereich erstellen
    cutout_mask = np.zeros_like(hsv_roi[:, :, 0])
    cv2.drawContours(cutout_mask, [valid_cutout_contour], -1, 255, thickness=cv2.FILLED)

    # 2. Maske für alles, was NICHT sauberes Silber ist, erstellen (potenzielle Defekte)
    silver_mask = cv2.inRange(hsv_roi, LOWER_SILVER, UPPER_SILVER)
    saubere_pixel_im_cutout = cv2.bitwise_and(silver_mask, silver_mask, mask=cutout_mask)
    potenzielle_defekte_maske = cv2.bitwise_xor(cutout_mask, saubere_pixel_im_cutout)

    # 3. Finde alle einzelnen "Inseln" (Konturen) in der potenziellen Defekt-Maske
    contours, _ = cv2.findContours(potenzielle_defekte_maske, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    echte_defekte_maske = np.zeros_like(potenzielle_defekte_maske)
    gesamte_defekt_flaeche = 0

    # 4. Iteriere über jede gefundene Insel und filtere sie
    for cnt in contours:
        flaeche = cv2.contourArea(cnt)
        
        # --- Filter A: Größen-Filter ---
        # Ignoriere winziges Rauschen
        if flaeche < MIN_DEFEKT_FLAECHE:
            continue # Springe zur nächsten Insel

        # --- Filter B: Farb-Filter ---
        # Erstelle eine kleine Maske nur für diese eine Insel
        temp_mask = np.zeros_like(potenzielle_defekte_maske)
        cv2.drawContours(temp_mask, [cnt], -1, 255, thickness=cv2.FILLED)
        
        # Berechne die Durchschnittsfarbe dieser Insel im Originalbild
        # WICHTIG: Wir benutzen hier hsv_roi, da unsere Farbwerte in HSV sind
        durchschnitts_farbe = cv2.mean(hsv_roi, mask=temp_mask)

        # Prüfe, ob die Durchschnittsfarbe im Bereich "echter Defekt" liegt
        h, s, v = durchschnitts_farbe[0], durchschnitts_farbe[1], durchschnitts_farbe[2]
        if not (LOWER_DEFECT_COLOR[0] <= h <= UPPER_DEFECT_COLOR[0] and
                LOWER_DEFECT_COLOR[1] <= s <= UPPER_DEFECT_COLOR[1] and
                LOWER_DEFECT_COLOR[2] <= v <= UPPER_DEFECT_COLOR[2]):
            # Diese Insel ist wahrscheinlich ein Kratzer oder eine Reflexion, kein blauer Rest
            continue # Springe zur nächsten Insel

        # Wenn eine Insel beide Filter überlebt, ist sie ein ECHTER Defekt
        # Zeichne sie in unsere finale Defekt-Maske ein
        cv2.drawContours(echte_defekte_maske, [cnt], -1, 255, thickness=cv2.FILLED)
        gesamte_defekt_flaeche += flaeche

    # 5. Finale Entscheidung basierend auf der Fläche der ECHTEN Defekte
    defekt_anteil = (gesamte_defekt_flaeche / flaeche_cutout) if flaeche_cutout > 0 else 0
    
    print(f"-> Messung Sauberkeit: Anteil echter Defekte = {defekt_anteil:.4%}")
    
    if defekt_anteil < ANTEIL_DEFEKT_FUER_NACHARBEIT:
        print("-> Ergebnis Sauberkeit: Cut-Out ist sauber.")
        return "io", echte_defekte_maske,potenzielle_defekte_maske, defekt_anteil
    else:
        print("-> Ergebnis Sauberkeit: Echte Defekte gefunden.")
        return "nachbearbeitung", echte_defekte_maske,potenzielle_defekte_maske, defekt_anteil