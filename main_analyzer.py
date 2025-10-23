import cv2
import os
import numpy as np 
from analysis.geometry_checker import check_geometry
from analysis.cleanliness_checker import check_cleanliness
from analysis.geometry_checker import LOWER_SILVER, UPPER_SILVER

# Konfiguration, die NUR die Analyse betrifft
ROI_Y_START = 880
ROI_Y_END = 1140
ROI_X_START = 80
ROI_X_END = 470

def run_full_analysis(image_path, output_folder):
    """
    Hauptfunktion: Lädt ein Bild und steuert den gesamten zweistufigen Analyseprozess.
    Gibt den Status und die Pfade zu den Ergebnisbildern zurück.
    """
    image = cv2.imread(image_path)
    if image is None:
        print(f"FEHLER: Bild konnte nicht geladen werden: {image_path}")
        return None, None

    # Analyse-Logik
    roi = image[ROI_Y_START:ROI_Y_END, ROI_X_START:ROI_X_END].copy()
    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    geometry_ok, contour, center, area = check_geometry(hsv_roi)

    if not geometry_ok:
        final_status = "nio"
        # Erstelle die Silber-Maske hier manuell, nur für den Fall, dass sie als Fehlerbild gespeichert werden soll
        mask_to_save = cv2.inRange(hsv_roi, LOWER_SILVER, UPPER_SILVER)
    else:
        final_status, mask_to_save = check_cleanliness(hsv_roi, contour, area)
    
    print(f"\n--- ENDGÜLTIGER STATUS: {final_status.upper()} ---")

    # Visuelle Ergebnisse für die Webseite speichern
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
    print(f"Analysebilder wurden im Ordner '{output_folder}' gespeichert.")

    result_images = {
        'kontur_bild': kontur_bild_path,
        'masken_bild': masken_bild_path
    }
    
    return final_status, result_images