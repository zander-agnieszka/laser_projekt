import cv2
import numpy as np

# --- KONFIGURATION ---
# Gib hier den Pfad zu einem guten Testbild an, auf dem der silberne
# Cut-Out klar zu sehen ist.
IMAGE_PATH = "IO_Pictures/image_2025-08-12_11-04-51.jpg" 
# =====================

def nothing(x):
    # Leere Funktion, wird für die Trackbar-Erstellung benötigt
    pass

# Lade das Bild
image = cv2.imread(IMAGE_PATH)
if image is None:
    print(f"Fehler: Bild unter {IMAGE_PATH} nicht gefunden.")
    exit()

# Erstelle ein Fenster für die Schieberegler
cv2.namedWindow('Trackbars')
cv2.resizeWindow('Trackbars', 600, 300)

# Erstelle die 6 Schieberegler für die untere und obere HSV-Grenze
cv2.createTrackbar('H_Lower', 'Trackbars', 0, 179, nothing)
cv2.createTrackbar('S_Lower', 'Trackbars', 0, 255, nothing)
cv2.createTrackbar('V_Lower', 'Trackbars', 0, 255, nothing)
cv2.createTrackbar('H_Upper', 'Trackbars', 179, 179, nothing)
cv2.createTrackbar('S_Upper', 'Trackbars', 255, 255, nothing)
cv2.createTrackbar('V_Upper', 'Trackbars', 255, 255, nothing)

# Setze Startwerte, die für "Silber" oft gut funktionieren
# (wenig Sättigung, hohe Helligkeit)
cv2.setTrackbarPos('V_Lower', 'Trackbars', 150)
cv2.setTrackbarPos('S_Upper', 'Trackbars', 50)


print("\n--- HSV Kalibrator ---")
print("Bewege die Regler, bis im 'Mask'-Fenster nur noch der gewünschte Bereich weiß ist.")
print("Drücke 'q' oder 'Esc', um das Programm zu beenden.")
print("Notiere dir die finalen Werte für H, S und V (Lower/Upper).")

while True:
    # Lese die aktuellen Positionen der Schieberegler
    h_lower = cv2.getTrackbarPos('H_Lower', 'Trackbars')
    s_lower = cv2.getTrackbarPos('S_Lower', 'Trackbars')
    v_lower = cv2.getTrackbarPos('V_Lower', 'Trackbars')
    h_upper = cv2.getTrackbarPos('H_Upper', 'Trackbars')
    s_upper = cv2.getTrackbarPos('S_Upper', 'Trackbars')
    v_upper = cv2.getTrackbarPos('V_Upper', 'Trackbars')

    # Erstelle die NumPy-Arrays für die Grenzen
    lower_bound = np.array([h_lower, s_lower, v_lower])
    upper_bound = np.array([h_upper, s_upper, v_upper])

    # Wandle das Bild in HSV um und erstelle die Maske
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_bound, upper_bound)

    # Zeige das Originalbild und die resultierende Maske an
    cv2.imshow('Original Image', image)
    cv2.imshow('Mask', mask)
    
    # Warte auf eine Tasteneingabe
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or key == 27: # 'q' oder Escape-Taste
        break

# Gib die finalen Werte aus, bevor das Programm endet
print("\n--- Finale Werte ---")
print(f"LOWER_BOUND = np.array([{h_lower}, {s_lower}, {v_lower}])")
print(f"UPPER_BOUND = np.array([{h_upper}, {s_upper}, {v_upper}])")

cv2.destroyAllWindows()