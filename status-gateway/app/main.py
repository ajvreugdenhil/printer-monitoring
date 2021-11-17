import os
import signal
import sys
import time
import printermodule
import printer

temperature_margin = 5

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
    # Define status parameters
    status = p.get_printer_endpoint("/api/printer")
    if status is not None:
        is_tool0_warming = status["temperature"]["tool0"]["actual"] < status["temperature"]["tool0"]["target"] - temperature_margin
        is_bed_warming = status["temperature"]["bed"]["actual"] < status["temperature"]["bed"]["target"] - temperature_margin
        is_error = status["state"]["flags"]["error"]
        is_closed_or_error = status["state"]["flags"]["closedOrError"]
        is_printing = status["state"]["flags"]["printing"]
        is_ready = status["state"]["flags"]["ready"]
        is_pausing = status["state"]["flags"]["pausing"]
        is_paused = status["state"]["flags"]["paused"]
        is_cancelling = status["state"]["flags"]["cancelling"]
        is_printing = status["state"]["flags"]["printing"]
    else:
        is_reachable = False

    # TODO: resend count
    # TODO: vibrations
    

m.send_message("red-off")
m.send_message("orange-blink")
m.send_message("green-off")
m.send_message("white-blink")
m.close()
print("Finished")