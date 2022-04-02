from django.db import models
import os
import uuid

# Create your models here.

def make_image(instanse,filename):
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
    phone = models.CharField('Telefoni', max_length=16,blank=True)
    parents_phone = models.CharField('Qarindoshining telefoni', max_length=16,blank=True)
    parents_info = models.CharField('Ismi ', max_length=16,blank=True)
    parents_status = models.CharField('Qarindoshligi', max_length=16,blank=True)
    #uuid = models.UUIDField(max_length=150, blank=True,null=True)
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    discount = models.PositiveIntegerField("Chegirma",default=0)
    debt = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to=make_image) # image not deleting!!!

    def __str__(self):
        return f"{self.name} {self.surname}"


class History(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    visit_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student}: {self.visit_date}"
