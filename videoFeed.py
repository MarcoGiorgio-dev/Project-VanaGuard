from camera import Camera
import cv2

camera = Camera()

def live_feed():
    frame = camera.get_frame()

    if frame is None:
        return None
    
    cv2.waitKey(1)
    cv2.imshow("Kamera Test", frame)

    return frame

def kill_feed():
    camera.stop()
    cv2.destroyAllWindows()
    
def start_feed():
    camera.start()

def get_processed_frame():
    frame = camera.get_frame()
    if frame is None:
        return None
    frame_resized = cv2.resize(frame, (640, 640))
    frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
    return frame_rgb
