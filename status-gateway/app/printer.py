import requests
import json 

class Printer:
    def __init__(self, ip, port, token) -> None:
        self.ip = ip
        self.port = port
        self.token = token

    def get_printer_endpoint(self, endpoint):
        try:
            r = requests.get(self.ip + ":" + str(self.port) + endpoint, headers={"X-Api-Key":self.token})
        except:
            return None
        
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            return None
