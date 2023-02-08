from picamera import PiCamera
import time

camera = PiCamera()
time.sleep(1)
camera.capture("pictures/img.jpg")
print("Done.")
