import configparser
import os

from DjangoWebcamStreaming.settings import BASE_DIR

class Config:
    def __init__(self):
        self.app_path = BASE_DIR
        self.config = configparser.ConfigParser()
        self.conf = os.path.join(self.app_path, 'src', 'data', 'config.ini')

    def get(self, args: str):
        self.config.read(self.conf)
        data = None

        CIP = str(self.config["SOCKET"]["CIP"])
        CPORT = int(self.config["SOCKET"]["CPORT"])
        SIP = str(self.config["SOCKET"]["SIP"])
        SPORT = int(self.config["SOCKET"]["SPORT"])
        BUFFSIZE = int(self.config["SOCKET"]["BUFFSIZE"])

        CAM = str(self.config["VIDEO"]["CAM"])
        VQ = int(self.config["VIDEO"]["VQ"])
        CUNK = eval(self.config["VIDEO"]["CUNK"])
        CDETECT = eval(self.config["VIDEO"]["CDETECT"])
        FRAME_RATE = int(self.config["VIDEO"]["FRAME_RATE"])

        data = eval(args)

        return data

    def _tmp_set(self, arg1: str, arg2: str, arg3):
        self.config.read(self.conf)
        self.config.set(arg1, arg2, str(arg3))
        with open(self.conf, "r") as conf_file:
            self.config.write(open(self.conf, "w"))

    def setCIP(self, index: str):
        self._tmp_set("SOCKET", "CIP", str(index))

    def setCPORT(self, index: int):
        self._tmp_set("SOCKET", "CPORT", str(index))