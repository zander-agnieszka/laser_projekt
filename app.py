import cv2
import os
from analysis.geometry_checker import check_geometry
from analysis.cleanliness_checker import check_cleanliness

# ===== HAUPT-KONFIGURATION =====
ROI_Y_START = 1225
ROI_Y_END = 1500
ROI_X_START = 180
ROI_X_END = 650
TEST_IMAGE_PATH = "Image/image_20250917_101430.jpg"
OUTPUT_FOLDER = "analyse_ergebnisse"
# ===============================

def run_full_analysis(image_path):
    """
    Hauptfunktion: Lädt ein Bild und steuert den gesamten zweistufigen Analyseprozess.
    """
    image = cv2.imread(image_path)
    if image is None:
        print(f"FEHLER: Bild konnte nicht geladen werden: {image_path}")
        return

    # 1. Bild auf ROI zuschneiden
    roi = image[ROI_Y_START:ROI_Y_END, ROI_X_START:ROI_X_END].copy()
    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    # 2. Gate 1: Geometrie prüfen
    geometry_ok, contour, center, area, silver_mask = check_geometry(hsv_roi)

    if not geometry_ok:
        final_status = "nio"
        mask_to_save = silver_mask
    else:
        # 3. Gate 2: Sauberkeit prüfen
        final_status, mask_to_save = check_cleanliness(hsv_roi, contour, silver_mask)
    
    print(f"\n--- ENDGÜLTIGER STATUS: {final_status.upper()} ---")

    # 4. Visuelle Ergebnisse für die Dokumentation speichern
    output_roi_image = roi.copy()
    if contour is not None:
        cv2.drawContours(output_roi_image, [contour], -1, (0, 255, 0), 2)
        if center is not None:
            cv2.circle(output_roi_image, center, 7, (0, 0, 255), -1)

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    cv2.imwrite(os.path.join(OUTPUT_FOLDER, "1_roi_ausschnitt.jpg"), roi)
    cv2.imwrite(os.path.join(OUTPUT_FOLDER, "2_silber_erkennung.jpg"), silver_mask)
    cv2.imwrite(os.path.join(OUTPUT_FOLDER, "3_kontur_und_mitte.jpg"), output_roi_image)
    if final_status != "nio":
         cv2.imwrite(os.path.join(OUTPUT_FOLDER, f"4_sauberkeit_{final_status}.jpg"), mask_to_save)

    print(f"Analysebilder wurden im Ordner '{OUTPUT_FOLDER}' gespeichert.")

# ===== Skript starten =====
if __name__ == "__main__":
    run_full_analysis(TEST_IMAGE_PATH)