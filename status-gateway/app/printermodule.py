import serial
import json
import os
import logging
from threading import Lock

startchar = '@'
endchar = '$'


class PrinterModule:
    def __init__(self, baudrate, serial_device, serial_range, printer_logger=None, gateway_logger=None) -> None:
        if printer_logger is None:
            logging.basicConfig(level=logging.INFO)
            self.printer_logger = logging.getLogger(__name__)
        else:
            self.printer_logger = printer_logger

        if gateway_logger is None:
            logging.basicConfig(level=logging.INFO)
            self.gateway_logger = logging.getLogger(__name__)
        else:
            self.gateway_logger = gateway_logger

        self.baudrate = baudrate
        self.serial_device = serial_device
        self.serial_range = serial_range
        self.port = None

        self.send_mutex = Lock()

    def send(self, message):
        encoded_message = (startchar + message + endchar).encode("utf-8")
        with self.send_mutex:
            try:
                self.port.write(encoded_message)
            except:
                self.gateway_logger.error("Did not send serial message: " + message)
                return None
            try:
                incoming_data = self.port.read_until(endchar).decode('utf-8')
            except serial.SerialTimeoutException as e:
                self.gateway_logger.error("Did not receive valid response in time: " + str(e))
                return None
            self.gateway_logger.debug("incoming_data: " + str(incoming_data))
            incoming_data_clean = incoming_data.split(startchar)[1].strip()[:-1]
            self.gateway_logger.debug("clean incoming data: " + incoming_data_clean)
        
            obj = json.loads(incoming_data_clean)
            if obj is None:
                self.gateway_logger.error("Could not parse: " + incoming_data_clean)
            return obj

    def start(self) -> bool:
        if self.serial_device is not None:
            raise NotImplemented
            # TODO
        elif self.serial_range is not None:
            serialrange = os.environ.get("SERIAL_RANGE")
            devpath = "/".join(serialrange.split("/")[:-1])
            devices = os.listdir(devpath)
            relevant_devices = []
            for device in devices:
                if device.startswith(serialrange.split("/")[-1]):
                    relevant_devices.append(devpath + '/' + device)
            if (len(relevant_devices) < 1):
                self.gateway_logger.error("No device found!")
                return False
            elif (len(relevant_devices) == 1):
                self.port = serial.Serial(
                    relevant_devices[0], self.baudrate, timeout=0.5)
            else:
                for device in relevant_devices:
                    try:
                        testport = serial.Serial(device, self.baudrate, timeout=1)
                    except serial.serialutil.SerialException:
                        continue
                    testport.flush()
                    message = (startchar + "get-acceleration" +
                            endchar).encode("utf-8")
                    testport.write(message)
                    try:
                        incoming_data = testport.readline()
                    except serial.serialutil.SerialException:
                        testport.close()
                        continue
                    testport.close()
                    if len(incoming_data) > 0:
                        incoming_data = incoming_data.strip()
                        data = {}
                        try:
                            incoming_data = incoming_data[1:-1]
                            data = json.loads(incoming_data)
                            if data["result"] == "ok" and self.port is None:  # HACK
                                self.port = serial.Serial(
                                    device, self.baudrate, timeout=0.5)
                        except:
                            continue

        if self.port is not None:
            self.port.flush()
            return True
        else:
            return False

    def close(self):
        if self.port is not None:
            self.port.close()
        else:
            self.gateway_logger.error("No port to close!")
