from videoFeed import start_feed, kill_feed, get_processed_frame, live_feed
from yoloFunctions import is_horse_down
import numpy as np
import onnxruntime as ort
import cv2
 
print("Starter YOLO test...")


yolo_session = ort.InferenceSession(
    "best.onnx",
    providers=["CPUExecutionProvider"]
)
 
input_name = yolo_session.get_inputs()[0].name
output_names = [o.name for o in yolo_session.get_outputs()]
 
print("YOLO model loaded.")
 
start_feed()
print("Kamera startet. Tryk 'q' for at afslutte.\n")
 
try:
    while True:
        live_feed()

        frame_resized = get_processed_frame()
 
        if frame_resized is None:
            print("Intet frame modtaget fra kamera — prøver igen.")
            continue
 
        img = frame_resized.transpose(2, 0, 1)
        img = np.expand_dims(img, axis=0).astype(np.float32) / 255.0
 
        outputs = yolo_session.run(output_names, {input_name: img})
        yolo_result = is_horse_down(outputs)
 
        if yolo_result == "laying":
            print("YOLO resultat: Hesten ligger ned.")
        elif yolo_result == "standing":
            print("YOLO resultat: Hesten står op.")
        else:
            print("YOLO resultat: Ingen konklusion endnu (for få frames).")
 
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("\nAfslutter test.")
            break
 
except KeyboardInterrupt:
    print("\nTest afbrudt af bruger.")
except Exception as e:
    print(f"Der opstod en fejl: {e}")
finally:
    kill_feed()
    print("Kamera stoppet. Test afsluttet.")
