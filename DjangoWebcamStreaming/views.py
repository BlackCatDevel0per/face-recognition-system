from django.shortcuts import render
from django.http import StreamingHttpResponse, HttpResponse, JsonResponse

from django.views.decorators import gzip

from main.models import Student

import time

#import cv2 
import socket, pickle

import os

import sqlite3

from settings import Config
SERVER_IP = Config().get("CIP")
SERVER_PORT = Config().get("CPORT")
BUFFSIZE = Config().get("BUFFSIZE")

global lock#
lock = None

def gen():
    global lock
    lock = False # stoping previous loop
    s_udp=socket.socket(socket.AF_INET , socket.SOCK_DGRAM)
    print("Socket server restarted!")
    #print("Waiting for connections..")
    while not lock:
        try:
            s_udp.bind((SERVER_IP, SERVER_PORT))
            lock = True # starting new loop
        except OSError:
            print("connect retrying..")
            time.sleep(0.1)

    while lock:
        bd=s_udp.recvfrom(BUFFSIZE)#
        #CIP = bd[1][0]
        data=bd[0]
        #print(data)
        jpeg=pickle.loads(data)
        #print(type(data))
        #frame = cv2.imdecode(data, cv2.IMREAD_COLOR)
        #cv2.imshow('server', data) #to open image
        # Encode the frame in JPEG format
    
        #jpeg = cv2.imencode('.jpg', frame)[1]
        if not lock:
            s_udp.close()
            print("Socket restart..")
            break
            
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

def index(request):
    return render(request, os.path.join('DjangoWebcamStreaming', 'index.html'))

@gzip.gzip_page
def video_feed(request): 
    return StreamingHttpResponse(gen(),
                                 content_type="multipart/x-mixed-replace; boundary=frame")

def check(request):
    #######
    
    # Get user data by id from sqlite connection
    conn = sqlite3.connect(os.path.join('src', 'data', 'tmp.db'))
    cur = conn.cursor()

    current_uuid = None

    cur.execute("SELECT * FROM tmp LIMIT 1;")
    current_uuid = cur.fetchone()
    if current_uuid:
        current_uuid = current_uuid[1]
    conn.close()
    #print(current_uuid)
    current_data = {}

    # SQL request
    if current_uuid:
        #print(current_uuid)
        try: # need replace "undefined"
            db = Student.objects.get(uuid__exact=current_uuid)
            current_data = {
            'name': db.name,
            'surname': db.surname,
            'address': db.address,
            'birth_date': db.birth_date,
            'phone': db.phone,
            'parents_phone': db.parents_phone,
            'parents_info': db.parents_info,
            'parents_status': db.parents_status,
            'discount': db.discount,
            'debt': db.debt,
            #'image': db.image,
            'uuid': db.uuid,
            }
        except Student.DoesNotExist as ed:
            print("DB err", ed)
        except Exception as e:
            print("DB err0", e)

    return JsonResponse(current_data)