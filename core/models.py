#import os
import uuid
from django.db import models

# Create your models here.

def make_image(instanse, filename):
    name = instanse.name
    id_ = instanse.uuid
    file_format = filename.split('.')[-1]
    new_file = f"{name}___{id_}.{file_format}"
    return new_file


class Student(models.Model):
    name = models.CharField('Ismi', max_length=25)
    surname = models.CharField('Familyasi', max_length=25)
    birth_date = models.DateField('Tugulgan kuni', blank=True, null=True)
    address = models.CharField('Manzili', max_length=355)
    phone = models.CharField('Telefoni', max_length=16, blank=True)
    parents_phone = models.CharField('Qarindoshining telefoni', max_length=16, blank=True)
    parents_info = models.CharField('Ismi ', max_length=16, blank=True)
    parents_status = models.CharField('Qarindoshligi', max_length=16, blank=True)
    #uuid = models.UUIDField(max_length=150, blank=True,null=True)
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    discount = models.PositiveIntegerField("Chegirma", default=0)
    debt = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to=make_image) # image not deleting!!!

    def __str__(self):
        return f"{self.name} {self.surname}"


class History(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
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
    FRAME_RATE = 2
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

    BUFFSIZE = models.PositiveIntegerField('BUFFSIZE', default=1000000)
    CIP = models.CharField('CIP', max_length=16, default='127.0.0.1')
    CPORT = models.PositiveIntegerField('CPORT', default=8080)
    SIP = models.CharField('SIP', max_length=16, default='127.0.0.1')
    SPORT = models.PositiveIntegerField('SPORT', default=8080)

    CAM = models.CharField('CAM', max_length=128, default='0')
    VQ = models.PositiveIntegerField('VQ', default=60)
    CUNK = models.CharField('CUNK', max_length=16, default='(255, 0, 0)')
    CDETECT = models.CharField('CDETECT', max_length=16, default='(0, 255, 0)')
    FRAME_RATE = models.PositiveIntegerField('FRAME_RATE', default=2)

    def __str__(self):
        return f"For cam: {self.CAM} | Use: {self.DEFAULT}"
