### This repository is strictly for submission of our exam project.

### Once everything is tried, tested, operational and edited, all of our python code will be submitted here, and turned over to our teachers for examination.
============================
# PROJECT VANGUARD DEPENDENCIES
============================
 
## RASPBERRY PI
 
Python packages:
pip install RPi.GPIO dht11 onnxruntime numpy opencv-python smbus mysql-connector-python adafruit-circuitpython-ads1x15 --break-system-packages
 
System packages:
sudo apt install python3-smbus i2c-tools libcamera-apps


## FLASK PC

Python packages:
pip install flask mysql-connector-python


## CUSTOM MODULES (must be in project folder) 

motor.py
pirSensor.py
videoFeed.py
yoloFunctions.py
db.py
humTemp.py
smokeADC.py


## DATABASE
MySQL Server (free, no signup required)
Ffter installing MySQL Server, create the heste_data database and sensor_readings table manually in the MySQL Server.
