from pirSensor import pir_setup, read_pir
from videoFeed import start_feed, kill_feed, get_processed_frame, close_camera
from time import time, sleep
import cv2

pir_setup()

camera_active = False
motion_timer = None
counter = 0

print("PIR sensor test startet — tryk Ctrl+C for at stoppe.\n")

try:
    while True:
        motion = read_pir()

        if motion:
            print("Bevægelse registreret.")
            counter = counter + 1
            print(f"Tæller:", counter)

            if not camera_active:
                print("Starter kamera.")
                start_feed()
                camera_active = True

            motion_timer = time()

        if camera_active:
            frame = get_processed_frame()
            if frame is not None:
                cv2.imshow("Kamera", frame)
                cv2.waitKey(1)

            if motion_timer and time() - motion_timer > 60:
                print("Ingen bevægelse i 1 minut — slukker kamera.")
                kill_feed()
                cv2.destroyAllWindows()
                camera_active = False
                motion_timer = None

        sleep(0.5)

except KeyboardInterrupt:
    print("\nTest afbrudt.")
finally:
    if camera_active:
        close_camera()
    cv2.destroyAllWindows()
    print("Ryddet op.")
