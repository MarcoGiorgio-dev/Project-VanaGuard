from camera import Camera
import cv2

camera = None

def start_feed():
    global camera
    camera = Camera()
    camera.start()

def get_processed_frame():
    if camera is None:
        return None
    frame = camera.get_frame()
    if frame is None:
        return None
    frame_resized = cv2.resize(frame, (640, 640))
    return frame_resized

def close_camera():
    global camera
    if camera is not None:
        camera.stop()
        camera = None
    cv2.destroyAllWindows()
