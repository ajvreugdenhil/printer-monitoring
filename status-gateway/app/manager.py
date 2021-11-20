import logging

from printer import Printer
from printermodule import PrinterModule


temperature_margin = 5
max_cold_temperature = 35
lampstates = {"red": "off", "orange": "blink", "green": "off", "white": "off"}

class PrinterManager:
    def __init__(self, printer: Printer, printermodule: PrinterModule, printer_logger, gateway_logger) -> None:
        self.printer = printer
        self.printermodule = printermodule
        self.printer_logger = printer_logger
        self.gateway_logger = gateway_logger

    def tick(self):
        # TODO: resend count
        # TODO: vibrations

        for color in lampstates:
            self.printermodule.send(color + "-" + lampstates[color])

        status = self.printer.get_printer_endpoint("/api/printer")
        if status is not None:
            is_reachable = True
            try:
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
            except KeyError:
                # unable to set right lamps
                self.gateway_logger.error("did not get proper data from printer")
                return

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