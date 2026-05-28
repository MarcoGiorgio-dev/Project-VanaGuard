import mysql.connector
import threading

DB_HOST = "10.187.222.169" 
DB_PORT = 3306

DB_USER = "vanaguard" 
DB_PASS = "gruppe7!"

DB_NAME = "heste_data"

def insert_sensor_reading_async(hum, temp, fan_on, window_open, smoke_detected, horse_down_counter):
    t = threading.Thread(target=insert_sensor_reading, args=(hum, temp, fan_on, window_open, smoke_detected, horse_down_counter))
    t.daemon = True
    t.start()

def get_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
    )

def insert_sensor_reading(hum, temp, fan_on, window_open, smoke_detected, horse_down_counter):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO sensor_readings
                (humidity, temperature, fan_on, window_open, smoke_detected, horse_down_count)
            VALUES
                (%s, %s, %s, %s, %s, %s)
        """, (hum, temp, fan_on, window_open, smoke_detected, horse_down_counter))
        conn.commit()
    except Exception as e:
        print(f"DB fejl: {e}")
    finally:
        try:
            cursor.close()
        except:
            pass
        try:
            conn.close()
        except:
            pass
