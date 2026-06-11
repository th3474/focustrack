
import serial
import csv
import time
from datetime import datetime

def computer_time():
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S.%f %Z")

def request_reset(ser):
    ser.write(b"r")
    ser.flush()
    print("Reset request sent to Arduino")

def start_logger():

    SERIAL_PORT = "/dev/cu.usbmodem14401" # DON'T FORGET TO UPDATE THIS!!!
    BAUD_RATE = 115200
    OUTPUT_FILE = "eye_movements.csv"

    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
    time.sleep(2)

    request_reset(ser)

    with open(OUTPUT_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow([
            "computer_time",
            "arduino_time_ms",
            "posX",
            "posY",
            "state",
            "rawH",
            "rawV",
            "deltaH",
            "deltaV"
        ])

        print("Logger started...")

        try:
            while True:
                line = ser.readline().decode("utf-8", errors="ignore").strip()

                if line.startswith("EVENT"):
                    parts = line.split(",")

                    if len(parts) == 9:
                        _, arduino_time, posX, posY, state, rawH, rawV, deltaH, deltaV = parts

                        writer.writerow([
                            computer_time(),
                            arduino_time,
                            posX,
                            posY,
                            state,
                            rawH,
                            rawV,
                            deltaH,
                            deltaV
                        ])

                        file.flush()
                        print("Saved:", arduino_time, posX, posY, state, rawH, rawV, deltaH, deltaV)

                elif line:
                    print("Arduino:", line)

        except KeyboardInterrupt:
            print("Logger stopped")

        finally:
            ser.close()