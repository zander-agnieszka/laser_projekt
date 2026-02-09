import cv2
import os
import numpy as np 
from analysis.geometry_checker import check_geometry
# from analysis.cleanliness_checker import check_cleanliness
from analysis.geometry_checker import LOWER_SILVER, UPPER_SILVER

from analysis.check_cleanliness import check_cleanliness

# Konfiguration, die NUR die Analyse betrifft
ROI_Y_START = 995
ROI_Y_END = 1235
ROI_X_START = 135
ROI_X_END = 515


def run_full_analysis(image_path, output_folder):
    """
    Hauptfunktion: Lädt ein Bild und steuert den gesamten zweistufigen Analyseprozess.
    Gibt den Status und ein Dictionary mit allen Analyse-Daten zurück.
    """                   
    # ... (Der Anfang der Funktion bis zur Analyse bleibt gleich) ...
    image = cv2.imread(image_path)
    if image is None: #...
        return None, None
    roi = image[ROI_Y_START:ROI_Y_END, ROI_X_START:ROI_X_END].copy()
    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    
    # --- Detaillierte Analyse-Daten sammeln ---
    analysis_data = {
        'geometry_passed': False,
        'gemessene_flaeche': 0,
        'gemessene_position': (0, 0),
        'unsauberer_anteil_prozent': 0,
        'kontur_bild': None,
        'masken_bild': None, 
        'error_reason': ""
    }
    alle_defekte_maske = None
    

    # Gate 1: Geometrie prüfen
    geometry_ok, contour, center, area, grund = check_geometry(hsv_roi)
    
    # Speichere die gemessenen Geometrie-Daten
    analysis_data['gemessene_flaeche'] = area if area is not None else 0
    analysis_data['gemessene_position'] = center if center is not None else (0,0)
   
    
    if not geometry_ok:
        final_status = "nio"
        analysis_data['geometry_passed'] = False
        analysis_data['error_reason'] = grund
        from analysis.geometry_checker import LOWER_SILVER, UPPER_SILVER
        mask_to_save = cv2.inRange(hsv_roi, LOWER_SILVER, UPPER_SILVER)
    else:
        analysis_data['geometry_passed'] = True
        
        # Gate 2: Sauberkeit prüfen
        # final_status, mask_to_save, unsauberer_anteil = check_cleanliness(hsv_roi, contour, area) # 1 Stufige Sauber -Prüfung
        final_status, mask_to_save, alle_defekte_maske, unsauberer_anteil = check_cleanliness(hsv_roi, roi, contour, area) # 2 Stufige Sauber -Prüfung
        analysis_data['unsauberer_anteil_prozent'] = unsauberer_anteil * 100 # In Prozent umrechnen
    
    print(f"\n--- ENDGÜLTIGER STATUS: {final_status.upper()} ---")

    # Visuelle Ergebnisse speichern
    os.makedirs(output_folder, exist_ok=True)
    output_roi_image = roi.copy()
    if contour is not None:
        cv2.drawContours(output_roi_image, [contour], -1, (0, 255, 0), 2)
        if center is not None:
            cv2.circle(output_roi_image, center, 7, (0, 0, 255), -1)

    kontur_bild_path = os.path.join(output_folder, f"kontur_{final_status}.jpg")
    masken_bild_path = os.path.join(output_folder, f"maske_{final_status}.jpg")
    
    cv2.imwrite(kontur_bild_path, output_roi_image)
    cv2.imwrite(masken_bild_path, mask_to_save)

    if alle_defekte_maske is not None:
        cv2.imwrite(os.path.join(output_folder, "4a_alle_potenziellen_defekte.jpg"), alle_defekte_maske)
    

    analysis_data['kontur_bild'] = kontur_bild_path
    analysis_data['masken_bild'] = masken_bild_path
    
    return final_status, analysis_data