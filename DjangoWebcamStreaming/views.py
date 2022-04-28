import os
import socket

from django.shortcuts import render
from django.http import StreamingHttpResponse, HttpResponse, JsonResponse

from django.views.decorators import gzip

from core.models import Student

import time

from .app_utils import VideoStreamSubscriber

print("Loading settings..")
from config import Config
SERVER_IP = Config().get("SIP")
if SERVER_IP == "None" or SERVER_IP == None:
    SERVER_IP = socket.gethostbyname(socket.gethostname())
SERVER_PORT = Config().get("SPORT")

global cuuid
cuuid = None
global current_uuid
current_uuid = None

def gen():
    try:
        receiver = VideoStreamSubscriber(SERVER_IP, SERVER_PORT)
        print("ZMQ connected: ", f"{SERVER_IP}:{SERVER_PORT}")

        while True:
            #print(type(data))
            #frame = cv2.imdecode(data, cv2.IMREAD_COLOR)
            #cv2.imshow('server', data) #to open image
            # Encode the frame in JPEG format
        
            #jpeg = cv2.imencode('.jpg', frame)[1]
            global cuuid
            cuuid, jpeg = receiver.receive()
            global current_uuid
            current_uuid = cuuid
                
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg + b'\r\n\r\n')
    except TimeoutError:
        receiver.close()
        print(f"ZMQ connection: {SERVER_IP}:{SERVER_PORT} down!")

    finally:
        receiver.close()
        print(f"ZMQ connection: {SERVER_IP}:{SERVER_PORT} restart..")

def index(request):
    return render(request, os.path.join('DjangoWebcamStreaming', 'index.html'))

@gzip.gzip_page
def video_feed(request): 
    return StreamingHttpResponse(gen(),
                                 content_type="multipart/x-mixed-replace; boundary=frame")

def check(request):
    #######


    current_uuid = cuuid
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