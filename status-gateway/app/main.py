import os
import signal
import sys
import time
import printermodule
import printer

temperature_margin = 5
max_cold_temperature = 35

stopflag = False

def signal_handler(sig, frame):
    print("Got signal: " + str(sig) + " Stopping...")
    global stopflag
    stopflag = True

print("Starting")

baudrate = os.environ.get("SERIAL_BAUD")
serdev = os.environ.get("SERIAL_DEVICE")
serrange = os.environ.get("SERIAL_RANGE")
m = printermodule.PrinterModule(baudrate, serdev, serrange)
port_available = m.start()
if not port_available:
    exit(1)

ip = os.environ.get("PRINTER_IP")
port = os.environ.get("PRINTER_PORT")
token = os.environ.get("PRINTER_TOKEN")
p = printer.Printer(ip, port, token)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

lampstates = {"red": "off", "orange": "blink", "green": "off", "white": "off"}

while not stopflag:
    for color in lampstates:
        m.send_message(color + "-" + lampstates[color])
    time.sleep(1)
    # TODO: resend count
    # TODO: vibrations
    
    status = p.get_printer_endpoint("/api/printer")
    if status is not None:
        is_reachable = True
        is_tool0_hot = status["temperature"]["tool0"]["actual"] > status["temperature"]["tool0"]["target"] - temperature_margin
        is_bed_hot = status["temperature"]["bed"]["actual"] > status["temperature"]["bed"]["target"] - temperature_margin
        is_tool0_warm = status["temperature"]["tool0"]["actual"] > max_cold_temperature
        is_bed_warm = status["temperature"]["bed"]["actual"] > max_cold_temperature
        is_error = status["state"]["flags"]["error"]
        is_closed_or_error = status["state"]["flags"]["closedOrError"]
        is_printing = status["state"]["flags"]["printing"]
        is_ready = status["state"]["flags"]["ready"]
        is_pausing = status["state"]["flags"]["pausing"]
        is_paused = status["state"]["flags"]["paused"]
        is_cancelling = status["state"]["flags"]["cancelling"]
        is_printing = status["state"]["flags"]["printing"]

        if is_error or is_closed_or_error:
            lampstates["red"] = "on"
        else:
            lampstates["red"] = "off"

        if not is_ready:
            lampstates["orange"] = "on"
        else:
            lampstates["orange"] = "off"

        if is_printing:
            if not is_bed_hot or not is_tool0_hot:
                lampstates["green"] = "blink"
            else:
                lampstates["green"] = "on"
        else:
            lampstates["green"] = "off"

        if is_cancelling or is_pausing:
            lampstates["white"] = "blink"
        elif is_paused or not is_printing:
            lampstates["white"] = "on"
        else:
            lampstates["white"] = "off"

    else:
        is_reachable = False
        lampstates["orange"] = "blink"
    

m.send_message("red-off")
m.send_message("orange-blink")
m.send_message("green-off")
m.send_message("white-blink")
m.close()
print("Finished")