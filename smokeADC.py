import smbus
from time import sleep
import signal

bus = smbus.SMBus(1)
ADS1115_ADDRESS = 0x48

def _timeout_handler(signum, frame):
    raise TimeoutError("I2C read timed out")

def smoke_check():
    try:
        signal.signal(signal.SIGALRM, _timeout_handler)
        signal.alarm(2) 

        config = [0xC3, 0x83]
        bus.write_i2c_block_data(ADS1115_ADDRESS, 0x01, config)
        sleep(0.01)

        data = bus.read_i2c_block_data(ADS1115_ADDRESS, 0x00, 2)
        value = (data[0] << 8) | data[1]

        signal.alarm(0)

        if value > 32767:
            value -= 65536

        print(f"Røgsensor ADC værdi: {value}")

        if value > 2500:
            print("ADVARSEL: RØG REGISTRERET --- LUKKER VINDUE OG SLUKKER BLÆSER!")
            return 1
        else:
            return 0

    except TimeoutError:
        print("Røgsensor timeout — springer over.")
        signal.alarm(0)
        return False
    except Exception as e:
        print(f"Røgsensor fejl: {e}")
        signal.alarm(0)
        return False
