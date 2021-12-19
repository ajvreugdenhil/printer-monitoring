from prometheus_client import start_http_server, Gauge
import logging
import json
import time

class MetricLogger:
    def __init__(self, printer_module, port, gateway_logger=None) -> None:
        if gateway_logger is None:
            logging.basicConfig(level=logging.INFO)
            self.gateway_logger = logging.getLogger(__name__)
        else:
            self.gateway_logger = gateway_logger
        self.port = port
        self.printer_module = printer_module
        start_http_server(self.port)
        self.last_tick_time = 0

        self.max_accel_x_gauge = Gauge("printmon_acceleration_max_x", "maximum acceleration for the X axis")
        self.max_accel_y_gauge = Gauge("printmon_acceleration_max_y", "maximum acceleration for the Y axis")
        self.max_accel_z_gauge = Gauge("printmon_acceleration_max_z", "maximum acceleration for the Z axis")
        self.avg_accel_x_gauge = Gauge("printmon_acceleration_avg_x", "average acceleration for the X axis")
        self.avg_accel_y_gauge = Gauge("printmon_acceleration_avg_y", "average acceleration for the Y axis")
        self.avg_accel_z_gauge = Gauge("printmon_acceleration_avg_z", "average acceleration for the Z axis")
        self.sample_count_gauge = Gauge("printmon_samplecount", "amount of samples of last measurement")
        self.tick_time_gauge = Gauge("printmon_ticktime", "time since last tick")

    def get_printer_module_metrics(self):
        data_obj = self.printer_module.send("get-acceleration")
        if data_obj is None:
            self.gateway_logger.error("Got none from printermodule. Is it connected?")
            return None
        else:
            if data_obj["result"] == "ok":
                if "content" in data_obj:
                    return data_obj["content"]
                else:
                    self.gateway_logger.error("Printermodule content did not contain right content: " + str(data_obj))
                    return None
            else:
                self.gateway_logger.error("Got not ok from printermodule: " + str(data_obj))
                return None
        
    def tick(self):
        data = self.get_printer_module_metrics()
        if data is not None:
            self.max_accel_x_gauge.set(data["MA_X"])
            self.max_accel_y_gauge.set(data["MA_Y"])
            self.max_accel_z_gauge.set(data["MA_Z"])
            self.avg_accel_x_gauge.set(data["AA_X"])
            self.avg_accel_y_gauge.set(data["AA_Y"])
            self.avg_accel_z_gauge.set(data["AA_Z"])
            self.sample_count_gauge.set(data["SC"])
            self.tick_time_gauge.set(round(time.time() * 1000) - self.last_tick_time)
        else:
            self.gateway_logger.warn("get_printer_module_metrics returned None")
        self.last_tick_time = round(time.time() * 1000)
