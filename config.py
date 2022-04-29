import os

from CORE.models import Settings

from django.db.utils import OperationalError

class Config:
    def __init__(self):

        self.data = True
        try:
            self.stngs = Settings.objects.get(DEFAULT=True)

        except OperationalError:
            print("Settings table does not exist!!!")
            self.data = None
        
        except Settings.DoesNotExist:
            print("No DEFAULT Settings")
            self.data = None

        # except TypeError:
        #     print("TypeError: Please check settings")
        #     SERVER_IP = None
        #     SERVER_PORT = None

        except Exception as e:
            print(e)
            self.data = None
        
        
    def get(self, args: str):

        if self.data: 
            SPORT = self.stngs.SPORT

            SIP = self.stngs.SIP

            CAM = self.stngs.CAM
            VQ = self.stngs.VQ
            
            CUNK = tuple(eval(self.stngs.CUNK))
            CDETECT = tuple(eval(self.stngs.CDETECT))
            
            RECOGNIZE_FRAME_RATE = int(self.stngs.RECOGNIZE_FRAME_RATE)

            WHISTORY_TIME_RANGE = dict(eval(self.stngs.WHISTORY_TIME_RANGE))

            self.data = eval(args)
            #print(data)

        return self.data
