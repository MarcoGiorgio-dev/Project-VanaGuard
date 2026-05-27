import urequests
import ujson
import machine
import time

import secrets
SERVER_URL = secrets.SERVER_URL

buzzer = machine.Pin(5, machine.Pin.OUT)
adc    = machine.ADC(machine.Pin(34))
adc.atten(machine.ADC.ATTN_11DB)

BATT_MAX_V    = 4.2
BATT_MIN_V    = 3.0
DIVIDER_RATIO = 2.0

POLL_EVERY   = 2000
REPORT_EVERY = 10000
BEEP_RATE    = 300

alarm_on    = False
buzzer_high = False

HEADERS = {
    "Content-Type": "application/json",
    "Connection":   "close"
}

def get_battery_percent():
    total = 0
    for _ in range(16):
        total += adc.read()
        time.sleep_ms(5)

    raw       = total / 16
    adc_volts = (raw / 4095) * 3.3
    batt_v    = adc_volts * DIVIDER_RATIO
    percent   = (batt_v - BATT_MIN_V) / (BATT_MAX_V - BATT_MIN_V) * 100

    return max(0, min(100, int(float(percent))))

def get_alarm_state():
    try:
        r    = urequests.get("http://192.168.0.33:5000" + "/api/status", headers=HEADERS)
        text = r.text
        r.close()
        data = ujson.loads(text)
        return bool(data.get("smoke_detected", False))
    except Exception as e:
        print("GET /api/status error:", e)
        return alarm_on

def send_battery(percent):
    try:
        r = urequests.post(
            SERVER_URL + "/api/battery",
            data=ujson.dumps({"battery": int(percent)}),
            headers=HEADERS
        )
        r.close()
        print("Battery:", percent, "%")
    except Exception as e:
        print("POST /api/battery error:", e)

def main():
    global alarm_on, buzzer_high

    last_poll   = 0
    last_report = 0
    last_beep   = 0

    print("Smoke alarm running.")

    while True:
        now = time.ticks_ms()

        if time.ticks_diff(now, last_poll) >= POLL_EVERY:
            last_poll = now
            new_state = get_alarm_state()
            if new_state != alarm_on:
                alarm_on = new_state
                print("Alarm ->", "ON" if alarm_on else "OFF")
                if not alarm_on:
                    buzzer.value(0)
                    buzzer_high = False

        if time.ticks_diff(now, last_report) >= REPORT_EVERY:
            last_report = now
            send_battery(get_battery_percent())

        if alarm_on:
            if time.ticks_diff(now, last_beep) >= BEEP_RATE:
                last_beep   = now
                buzzer_high = not buzzer_high
                buzzer.value(1 if buzzer_high else 0)

        time.sleep_ms(50)

main()
