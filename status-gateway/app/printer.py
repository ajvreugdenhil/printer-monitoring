import requests
import json
import logging


class Printer:
    def __init__(self, ip, port, token, printer_logger=None, gateway_logger=None) -> None:
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

        self.ip = ip
        self.port = port
        self.token = token

    def get_printer_endpoint(self, endpoint):
        # TODO: cut retry time
        try:
            r = requests.get(self.ip + ":" + str(self.port) +
                             endpoint, headers={"X-Api-Key": self.token})
        except:
            return None

        if r.status_code == 200:
            return json.loads(r.content)
        else:
            return None

    def set_printer_message(self, message: str) -> bool:
        clean_message = ''.join(
            [i for i in message if i.isalnum() or i == ' '])
        payload = json.dumps({"command": "M117 " + clean_message})

        endpoint = "/api/printer/command"
        url = self.ip + ":" + str(self.port) + endpoint
        self.gateway_logger.debug("trying to contact %s", url)
        try:
            r = requests.post(url,
                              headers={"X-Api-Key": self.token,
                                       'content-type': 'application/json'},
                              data=payload)
        except:
            self.gateway_logger.error("Connection to %s failed", url)
            return False

        if r.status_code != 204:
            self.gateway_logger.error(
                "Setting message for %s failed: %d", url, r.status_code)
            return False

        return True
