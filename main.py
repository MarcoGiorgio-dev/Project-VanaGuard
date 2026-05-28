from motor import open_window, close_window, turn_on_fan, turn_off_fan, fan_setup, janitor
from humTemp import get_humTemp
from pirSensor import pir_setup, read_pir
from time import sleep, time
from videoFeed import live_feed, kill_feed, start_feed, get_processed_frame, close_camera
from yoloFunctions import is_horse_down
from smokeADC import smoke_check
from db import insert_sensor_reading, insert_sensor_reading_async
import os
import numpy as np
import onnxruntime as ort

pir_setup()
fan_setup(9)
smoke_detected = None

horse_down_counter = 0
horse_was_laying = False
camera_active = False
motion_timer = None
fan_on = False
window_open = False
hum = 0
temp = 0
sensor_timer = time()
laying_frames = 0
laying_threshold = 3
smoke_timer = time()

os.environ["LIBCAMERA_LOG_LEVELS"] = "ERROR"

_last_msg = None
_last_msg_time = 0

def smart_print(msg):
  global _last_msg, _last_msg_time
  if msg != _last_msg or time() - _last_msg_time > 1800:
    print(msg)
    _last_msg = msg
    _last_msg_time = time()

yolo_session = ort.InferenceSession(
    "best.onnx",
    providers=["CPUExecutionProvider"]
)

input_name = yolo_session.get_inputs()[0].name
output_names = [o.name for o in yolo_session.get_outputs()]

try:
  while True:
    if time() - smoke_timer > 30:
      smoke_detected = smoke_check()
      smoke_timer = time()

    if smoke_detected:
      close_window()
      turn_off_fan(9)
      insert_sensor_reading_async(hum, temp, fan_on, window_open, smoke_detected, horse_down_counter)

    else:
      if time() - sensor_timer > 10:
        new_hum, new_temp = get_humTemp()
        sensor_timer = time()

        if new_hum is not None and new_temp is not None:
          hum, temp = new_hum, new_temp
        else:
          smart_print("Sensoraflæsning fejlede, beholder tidligere værdier.")

        insert_sensor_reading_async(hum, temp, fan_on, window_open, smoke_detected, horse_down_counter)

      if temp >= 25 and not fan_on:
        smart_print("Høj temperatur, tænder blæser.")
        turn_on_fan(9)
        fan_on = True
      elif temp < 25 and fan_on:
        smart_print("Temperatur acceptabel, slukker blæser.")
        turn_off_fan(9)
        fan_on = False

      if hum >= 60 and not window_open:
        smart_print("Høj fugtighed, åbner vindue.")
        open_window()
        window_open = True
      elif hum < 60 and window_open:
        smart_print("Acceptabel luftfugtighed opnået, lukker vindue.")
        close_window()
        window_open = False

      if not fan_on and not window_open and temp < 25 and hum < 60:
        smart_print("Forhold er optimale, ingen handling påkrævet.")

    motion = read_pir()

    if not motion:
      if camera_active:
        if time() - motion_timer > 60:
          smart_print("Ingen bevægelse i 1 minut — slukker kamera.")
          kill_feed()
          camera_active = False
          motion_timer = None

    else:
      if motion_timer is None:
        motion_timer = time()

      if not camera_active:
        smart_print("Bevægelse registreret — starter kamera.")
        start_feed()
        camera_active = True

      if time() - motion_timer < 60:

        frame_resized = get_processed_frame()

        if frame_resized is None:
          continue

        img = frame_resized.transpose(2, 0, 1)
        img = np.expand_dims(img, axis=0).astype(np.float32) / 255.0

        outputs = yolo_session.run(output_names, {input_name: img})
        yolo_result = is_horse_down(outputs)

        if yolo_result is None:
          continue

        if yolo_result == "laying":
          smart_print("YOLO resultat: Hesten ligger ned.")
          laying_frames += 1

          if laying_frames >= laying_threshold:
            if not horse_was_laying:
              horse_down_counter += 1
              horse_was_laying = True

        elif yolo_result == "standing":
          smart_print("YOLO resultat: Hesten står op.")
          laying_frames = 0
          horse_was_laying = False

        else:
          smart_print("YOLO resultat: Ingen konklusion endnu (for få frames).")

      else:
        smart_print("Ingen bevægelse i 1 minut — slukker kamera.")
        kill_feed()
        camera_active = False
        motion_timer = None

    sleep(0.5)
except KeyboardInterrupt:
  print("Program afbrudt, lukker ned.")
except Exception as e:
  print(f"Der opstod en fejl: {e}")
finally:
    if camera_active:
        close_camera()
    janitor()
  
