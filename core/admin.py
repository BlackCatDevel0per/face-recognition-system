from django.contrib import admin
from .models import Student, History, Settings
# Register your models here.

@admin.register(Student)
class Student(admin.ModelAdmin):
	list_display = ('surname', 'name', 'phone', 'address', 'birth_date', 'debt', 'discount')

@admin.register(History)
class History(admin.ModelAdmin):
	list_display = ('student', 'visit_date')

@admin.register(Settings)
class Settings(admin.ModelAdmin):
	list_display = ('CAM', 'DEFAULT', 'CUNK', 'CDETECT', 'WHISTORY_TIME_RANGE')
	