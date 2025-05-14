from picamera2 import Picamera2
import time
from datetime import datetime

picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration())

picam2.start()
time.sleep(2)  # kurze Wartezeit

filename = datetime.now().strftime("image_%Y-%m-%d_%H-%M-%S.jpg")
picam2.capture_file(filename)

print(f"Bild gespeichert als {filename}")