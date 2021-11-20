import os
import signal
import sys
import time
import logging

import manager
import printermodule
import printer

printer_logger_file = "printer_logs.txt"

stopflag = False


def signal_handler(sig, frame):
    global stopflag
    stopflag = True


def getlogger(logger_name=None):
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

    if logger_name is None:
        logger = logging.getLogger(__name__)
    else:
        logger = logging.getLogger(logger_name)

    return logger

gateway_logger = getlogger("gateway_logger")
printer_logger = getlogger("printer_logger")
printer_logger_file_handler = logging.FileHandler(printer_logger_file)
printer_logger.addHandler(printer_logger_file_handler)

baudrate = os.environ.get("SERIAL_BAUD")
serdev = os.environ.get("SERIAL_DEVICE")
serrange = os.environ.get("SERIAL_RANGE")
m = printermodule.PrinterModule(baudrate, serdev, serrange, printer_logger, gateway_logger)
port_available = m.start()
if not port_available:
    exit(1)

ip = os.environ.get("PRINTER_IP")
port = os.environ.get("PRINTER_PORT")
token = os.environ.get("PRINTER_TOKEN")
p = printer.Printer(ip, port, token, printer_logger, gateway_logger)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

manager = manager.PrinterManager(p, m, printer_logger, gateway_logger)

gateway_logger.info("Starting")

if not p.set_printer_message("Gateway started"):
    gateway_logger.error("Could not set initial printer message")

while not stopflag:
    manager.tick()
    time.sleep(1)

gateway_logger.info("Stopping...")

m.send("red-off")
m.send("orange-blink")
m.send("green-off")
m.send("white-blink")
m.close()

gateway_logger.info("Stopped")
