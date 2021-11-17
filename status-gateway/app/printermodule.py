import serial
import json
import os

startchar = '@'
endchar = '$'

class PrinterModule:
    def __init__(self, baudrate, serial_device, serial_range) -> None:
        self.baudrate = baudrate
        self.serial_device = serial_device
        self.serial_range = serial_range
        self.port = None

    def send_message(self, message):
        encoded_message = (startchar + message + endchar).encode("utf-8")
        try:
            self.port.write(encoded_message)
            incoming_data = self.port.readline().decode().strip()
        except:
            return None
        if (len(incoming_data) >= 2):
            if (incoming_data[0] == startchar and incoming_data[-1] == endchar):
                return incoming_data[1:-1]
            else:
                return None

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
                print("No ttyusb found!")
                return False
            elif (len(relevant_devices) == 1):
                self.port = serial.Serial(relevant_devices[0], self.baudrate, timeout=0.05)
            else:
                for device in relevant_devices:
                    testport = serial.Serial(device, self.baudrate, timeout=1)
                    testport.flush()
                    message = (startchar + "get-acceleration" +  endchar).encode("utf-8")
                    testport.write(message)
                    incoming_data = testport.readline()
                    testport.close()
                    if len(incoming_data) > 0:
                        incoming_data = incoming_data.strip()
                        data = {}
                        try:
                            incoming_data = incoming_data[1:-1]
                            data = json.loads(incoming_data)
                            if data["result"] == "ok" and self.port is None: # HACK
                                self.port = serial.Serial(device, self.baudrate, timeout=0.05)
                        except:
                            continue
        
        if self.port is not None:
            return True
        else:
            return False
        
    def close(self):
        if self.port is not None:
            self.port.close()
        else:
            print("No port to close!")