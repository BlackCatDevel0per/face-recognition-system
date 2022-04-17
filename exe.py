import os
import time
import shlex
import psutil
import subprocess

import pystray

from PIL import Image, ImageDraw, UnidentifiedImageError



lockfile = 'app.lock'
def run_check():
    txt = None
    if not os.path.exists(lockfile):
        with open(lockfile, 'w') as lf:
            lf.write(str(os.getpid()))
    with open(lockfile, 'r+') as lf:
        txt = lf.read()
        if not txt:
            lf.write(str(os.getpid()))

    try:
        pid = int(txt)
    except ValueError:
        os.remove(lockfile)
        exit(1)
    if psutil.pid_exists(pid):
        print("Programm already running:", pid, 'current:', os.getpid())
        exit(1)
    else:
        with open(lockfile, 'w') as lf:
            lf.write(str(os.getpid()))        

ICON_PATH = os.path.join(os.getcwd(), "staticfiles", "DjangoWebcamStreaming", "images", "favicon.ico")
NAME = "FRS"
ACT_RUN = "RUN"
ACT_STOP = "STOP"
ACT_EXIT = "EXIT"

def startup_actions():
    try:
        import sqlite3

        conn = sqlite3.connect(os.path.join(os.getcwd(), 'src', 'data', 'tmp.db'))
        cur = conn.cursor()


        cur.execute("""
                    CREATE TABLE IF NOT EXISTS "tmp" (
                    "id"    INTEGER NOT NULL UNIQUE,
                    "UUID"  INTEGER UNIQUE,
                    PRIMARY KEY("id" AUTOINCREMENT)
                    );
                    """)

        cur.execute("""DELETE FROM tmp;""")

        ldir = os.listdir(os.path.join("src", "images"))
        cuuid = None
        for p in ldir:
           if "___" in p and p.endswith(".jpg"):
              cuuid = p.split("___")[1].replace(".jpg", "")
              print("Setted for startpage:", cuuid)
              cur.execute("""INSERT INTO tmp VALUES(1, ?);
                                              """, (cuuid,))

              conn.commit()
              conn.close()
              break
           else:
              print("Bad filename: ", p)
    except Exception as e:
        print(eyy)

from pystray import Icon as icon, Menu as menu, MenuItem as item

def create_image(width: int=64, height: int=64, color1: str='black', color2: str='white'):
    # Generate an image and draw a pattern
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle(
        (width // 2, 0, width, height // 2),
        fill=color2)
    dc.rectangle(
        (0, height // 2, width // 2, height),
        fill=color2)

    return image

try:
    ICON = Image.open(ICON_PATH)
    ICON.load()
except UnidentifiedImageError:
    ICON = create_image()
except FileNotFoundError:
    ICON = create_image()

if not ICON_PATH:
    ICON_PATH = create_image()

global cv_client
global django_server
global pool
pool = False

def on_clicked(icon, item):
    global cv_client
    global django_server
    global pool
    if not pool:
        startup_actions()
        cv_client = subprocess.Popen(["""WPy64-38100\python-3.8.10.amd64\python.exe""", "socket_cv2_client.py"])
        django_server = subprocess.Popen(["""WPy64-38100\python-3.8.10.amd64\python.exe""", "manage.py", "runserver"])
        print("Process started!")
        pool = True
    else:
        print("Process already running!!!")

def on_stop(icon, item):
    global cv_client
    global django_server
    global pool
    if pool:
        """
        try:
            psutil.Process(cv_client.pid).kill()
        except psutil.NoSuchProcess:
            pass
        try:
            psutil.Process(django_server.pid).kill()
        except psutil.NoSuchProcess:
            pass
        """
        subprocess.Popen(shlex.split("taskkill /F /T /PID %d" % cv_client.pid)) # psutil
        subprocess.Popen(shlex.split("taskkill /F /T /PID %d" % django_server.pid)) # psutil
        print("Process killed!")
        pool = False
    else:
        print("Process is not running!")

def on_exit(icon, item):
    on_stop(icon, item)
    icon.stop()

ic = icon(NAME, ICON, menu=menu(
    item(
        ACT_RUN,
        on_clicked),
    item(
        ACT_STOP,
        on_stop),
    item(
        ACT_EXIT,
        on_exit)))


if os.name == 'nt':
    run_check()
    ic.run()
    os.remove(lockfile)
