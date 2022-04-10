import cv2
import face_recognition
import numpy as np

from cv import * #dinfo

import os

import sqlite3

import pytz
from time import time
from datetime import datetime, timedelta

import socket, pickle
import numpy as np

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DjangoWebcamStreaming.settings")
django.setup()

from config import Config

from core.models import History

def main():
    # Socket Server

    CAM = Config().get("CAM")
    CLIENT_IP = Config().get("SIP")
    CLIENT_PORT = Config().get("SPORT")
    BUFFSIZE = Config().get("BUFFSIZE")
    VQ = Config().get("VQ")
    CUNK = Config().get("CUNK")[::-1]
    CDETECT = Config().get("CDETECT")[::-1]
    FRAME_RATE = Config().get("FRAME_RATE")

    WHISTORY_TIME_RANGE = Config().get("WHISTORY_TIME_RANGE")
    WHOURS, WMINUTES = WHISTORY_TIME_RANGE.get('hours'), WHISTORY_TIME_RANGE.get('minutes')

    s_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s_udp.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, BUFFSIZE)#

    print("*"*42)
    print(f"Server running at: http://{CLIENT_IP}:{CLIENT_PORT}")
    print("*"*42)

    #video = cv2.VideoCapture(0)
    video = cv2.VideoCapture(CAM) # my ip cam
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
        success, frame = video.read()

        #if not success:
        #        return False

        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)###

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]


        if time_elapsed > 1./FRAME_RATE: # don't use continue
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
                    # socket tcp request
                    #print(cuuid)
                    ###
                    with sqlite3.connect(os.path.join('src', 'data', 'tmp.db')) as conn:
                        cur = conn.cursor()

                        cur.execute("""UPDATE tmp SET UUID = ? WHERE id = 1;
                                    """, (cuuid,))
                        conn.commit()
                        #conn.close()
                        #print('DETECT')

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
        #buffer = cv2.imencode(".jpg", frame)[1] # default quality
        x_as_bytes = pickle.dumps(buffer)
        s_udp.sendto((x_as_bytes), (CLIENT_IP, CLIENT_PORT)) # need bytes size check or/& compress them how it can

    video.release()



if __name__ == '__main__':
    main()


