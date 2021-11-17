import requests
import json


class Printer:
    def __init__(self, ip, port, token) -> None:
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
        print(payload)

        endpoint = "/api/printer/command"
        try:
            r = requests.post(self.ip + ":" + str(self.port) + endpoint,
                              headers={"X-Api-Key": self.token,
                                       'content-type': 'application/json'},
                              data=payload)
            print(r.status_code)
            print(r.content)
        except:
            return False

        if r.status_code != 204:
            return False

        return True
