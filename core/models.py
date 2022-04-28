import os
import uuid
from django.db import models

from DjangoWebcamStreaming.settings import BASE_DIR

toast_cam_script_path = 'UNKNOWN'
if os.name == 'nt':
    toast_cam_script_path = os.path.join(BASE_DIR, 'toast_cameras.bat')
elif os.name == 'posix':
    toast_cam_script_path = os.path.join(BASE_DIR, 'toast_cameras.py')

# Create your models here.

def make_image(instanse, filename):
    name = instanse.name
    id_ = instanse.uuid
    file_format = filename.split('.')[-1]
    new_file = f"{name}___{id_}.{file_format}"
    return new_file


class Student(models.Model):
    name = models.CharField('Name', max_length=25)
    surname = models.CharField('Surname', max_length=25)
    birth_date = models.DateField('Birth date', blank=True, null=True)
    address = models.CharField('Address', max_length=355)
    phone = models.CharField('Phone', max_length=16, blank=True)
    parents_phone = models.CharField('Parents phone', max_length=16, blank=True)
    parents_info = models.CharField('Parents info', max_length=16, blank=True)
    parents_status = models.CharField('Parents status', max_length=16, blank=True)
    #uuid = models.UUIDField(max_length=150, blank=True,null=True)
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    discount = models.PositiveIntegerField("Discount", default=0)
    debt = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to=make_image)

    def __str__(self):
        return f"{self.name} {self.surname}"


class History(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE) # student uuid
    visit_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student}: {self.visit_date}"

class Settings(models.Model):
    """
    [SOCKET]
    BUFFSIZE = 1000000
    CIP = 127.0.0.1
    CPORT = 8080
    SIP = 127.0.0.1
    SPORT = 8080

    [VIDEO]
    CAM = http://192.168.1.103:4747/video
    VQ = 60
    CUNK = (255, 0, 0)
    CDETECT = (0, 255, 0)
    RECOGNIZE_FRAME_RATE = 2
    """
    DEFAULT = models.BooleanField('DEFAULT', default=False)

    def save(self, *args, **kwargs): # Unique default
        if self.DEFAULT:
            try:
                temp = Settings.objects.get(DEFAULT=True)
                if self != temp:
                    temp.DEFAULT = False
                    temp.save()
            except Settings.DoesNotExist:
                pass
        super(Settings, self).save(*args, **kwargs)

    SIP = models.CharField('SIP', max_length=16, help_text='Server IP (Face Recognition)', default='127.0.0.1')
    SPORT = models.PositiveIntegerField('SPORT', help_text='Server PORT (Face Recognition)', default=8080)

    CAM = models.CharField('CAM', max_length=128, help_text=f'Server Camera IP (Face Recognition)\nCan use system camera by index (run to get cam index: {toast_cam_script_path} )', default='0')

    VQ = models.PositiveIntegerField('VQ', help_text='Video Quality in %', default=60)
    CUNK = models.CharField('CUNK', max_length=16, help_text='Color for frame if unknown people detected', default='(255, 0, 0)')
    CDETECT = models.CharField('CDETECT', max_length=16, help_text='Colour for frame if known people detected', default='(0, 255, 0)')
    RECOGNIZE_FRAME_RATE = models.PositiveIntegerField('RECOGNIZE_FRAME_RATE', help_text='Recognize frames count per second', default=2)

    WHISTORY_TIME_RANGE = models.CharField('WHISTORY_TIME_RANGE', help_text='Write History Time Range', max_length=64, default="{'hours': 1, 'minutes': 0}")
    
    def __str__(self):
        return f"CAM: {self.CAM} | USE: {self.DEFAULT}"
