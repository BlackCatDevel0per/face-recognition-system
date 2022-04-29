import cv2
import face_recognition
import numpy as np

from cv import * #dinfo

import os

import pytz
from time import time
from time import sleep
from datetime import datetime, timedelta

import socket
from imutils.video import VideoStream
import imagezmq

import numpy as np

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DjangoWebcamStreaming.settings")
django.setup()

from config import Config

from core.models import History


def main():
    # Socket Server

    CAM = Config().get("CAM")
    SERVER_IP = socket.gethostbyname(socket.gethostname())
    SERVER_PORT = Config().get("SPORT")
    VQ = Config().get("VQ")
    CUNK = Config().get("CUNK")[::-1]
    CDETECT = Config().get("CDETECT")[::-1]
    RECOGNIZE_FRAME_RATE = Config().get("RECOGNIZE_FRAME_RATE")

    WHISTORY_TIME_RANGE = Config().get("WHISTORY_TIME_RANGE")
    WHOURS, WMINUTES = WHISTORY_TIME_RANGE.get('hours'), WHISTORY_TIME_RANGE.get('minutes')

    sender = imagezmq.ImageSender(f"tcp://*:{SERVER_PORT}", REQ_REP=False)

    print("*"*42)
    print(f"Server running at: http://{SERVER_IP}:{SERVER_PORT}")
    print("*"*42)

    #video = cv2.VideoCapture(0)
    video = VideoStream(CAM) # my ip cam
    video.start()
    sleep(2.0)
    print("Input stream opened!")
    ldir = os.listdir(os.path.join("src", "images"))

    if not ldir:
        print("Directory is empty!!!")
        raise OSError

    try:
        KFE = []
        KNOWN_FACE_FILENAMES = []
        for p in ldir:
            # Path.with_suffix from pathlib.Path need
            if "___" in p and p.endswith(".jpg"):
                # Get face image
                image = face_recognition.load_image_file(os.path.join("src", "images", p)) # recommended max size 1944x2592 and unturned
                # Get face image encoding
                face_encoding = face_recognition.face_encodings(image)[0]
                KFE.append(face_encoding)
                # Appending list without .jpg file extension
                KNOWN_FACE_FILENAMES.append(p.replace(".jpg", ""))
                print("Added:", p)
            else:
                print("Skiped:", p)
    # Except no face
    except IndexError as e:
        print(e)
        print("Maybe image is not correct")
        #sys.exit(1) # stops code execution in my case you could handle it differently
        exit(1) # stops code execution in my case you could handle it differently

    if not KNOWN_FACE_FILENAMES:
        print("NO DATA TO RECOGNIZE!")
        raise OSError

    cuuid = None

    KNOWN_FACE_ENCODINGS = KFE


    # Initialize some variables
    face_locations = []
    face_encodings = []
    face_names = []

    # frame rate to compute
    prev = 0


    while True: ###


        #########################

        # Grab a single frame of video
        time_elapsed = time() - prev
        frame = video.read()

        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)###

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]


        if time_elapsed > 1./RECOGNIZE_FRAME_RATE: # don't use continue
            prev = time()

            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []
            name = "Unknown"
            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(KNOWN_FACE_ENCODINGS, face_encoding)

                # # If a match was found in KNOWN_FACE_ENCODINGS, just use the first one.
                # if True in matches:
                #     first_match_index = matches.index(True)
                #     name = KNOWN_FACE_FILENAMES[first_match_index]

                # Or instead, use the known face with the smallest distance to the new face
                face_distances = face_recognition.face_distance(KNOWN_FACE_ENCODINGS, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = KNOWN_FACE_FILENAMES[best_match_index].split('___')[0]
                    current_uuid = KNOWN_FACE_FILENAMES[best_match_index].split('___')[1]


                face_names.append(name)


        ######################################
        colorbgr = CUNK
        if name != "Unknown":
            colorbgr = CDETECT

            if current_uuid:
                if cuuid != current_uuid:
                    cuuid = current_uuid
                    #print(current_uuid)

                    visit_dates = History.objects.all().filter(student_id=current_uuid).values_list('visit_date', flat=True)

                    if visit_dates:
                        nearest = lambda lst, target: min(lst, key=lambda x: abs(x-target))
                        last_visit_date = nearest(visit_dates, datetime.now().replace(tzinfo=pytz.UTC))

                    else:
                        last_visit_date = None
                    
                    print(last_visit_date)

                    # print(last_visit_date) # <class 'datetime.datetime'>
                    # print(type(last_visit_date))

                    if last_visit_date:
                        if last_visit_date.replace(tzinfo=None) + timedelta(hours=WHOURS, minutes=WMINUTES) <= datetime.now(): # tzinfo=<UTC>
                            # Add visit date to history
                            History.objects.create(student_id=current_uuid, visit_date=datetime.now())
                            print("Bye! See you next time!")
                        else:
                            print("Hi! I saw you recently!")
                    
                    else:
                        History.objects.create(student_id=current_uuid, visit_date=datetime.now())
                        print("Hi! I see you for the first time!")

                    ###

        frame = dinfo(
                      frame=frame, 
                      zfln=zip(face_locations, face_names), 
                      name=name, colorbgr=colorbgr
                      )

        #3#
        #cv2.imshow('streaming',frame)
        # Encode the frame in JPEG format with changing quality
        buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), VQ])[1] # lower quality
        sender.send_jpg(cuuid, buffer)

    video.stop()
    sender.close()



if __name__ == '__main__':
    main()


