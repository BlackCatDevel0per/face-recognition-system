import os
import sys
import time
import shlex
import psutil
import tempfile
import subprocess

import webbrowser

import pystray

from PIL import Image, ImageDraw, UnidentifiedImageError

# pyinstaller --icon=staticfiles\STREAMING\images\favicon.ico --onefile --windowed run_tray.py

lockfile = os.path.join(tempfile.gettempdir(), 'FRS_TRAY.lock')
logfile = open(os.path.join(tempfile.gettempdir(), 'FRS.log'), 'w')
def run_check():
    txt = None
    if not os.path.exists(lockfile):
        with open(lockfile, 'w') as lf:
            lf.write(str(os.getpid()))
            return True #
    with open(lockfile, 'r+') as lf:
        txt = lf.read()
        if not txt:
            print("W: lockfile is empty!")
            lf.write(str(os.getpid()))
            return True #

    try:
        pid = int(txt)
    except ValueError:
        os.remove(lockfile)
        sys.exit(1)
    if psutil.pid_exists(pid):
        print("Programm already running:", pid, 'current:', os.getpid())
        raise OSError("Programm already running!")
        sys.exit(0)
    else:
        with open(lockfile, 'w') as lf:
            lf.write(str(os.getpid()))        

ICON_PATH = os.path.join(os.getcwd(), "staticfiles", "STREAMING", "images", "favicon.ico")
NAME = "FRS"
ACT_RUN = "RUN"
ACT_RESTART = "RESTART"
ACT_STOP = "STOP"
ACT_EXIT = "EXIT"

def startup_actions():
    try:
        ldir = os.listdir(os.path.join("src", "images"))
        cuuid = None
        for p in ldir:
           if "___" in p and p.endswith(".jpg"):
              cuuid = p.split("___")[1].replace(".jpg", "")
              break
           else:
              print("Bad filename: ", p)

    except Exception as e:
        print(e)

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

def on_run(icon, item):
    global cv_client
    global django_server
    global pool
    if not pool:
        startup_actions()
        if os.name == 'nt':
            cv_client = subprocess.Popen(["""WPy64-38100\python-3.8.10.amd64\python.exe""", "zmq_cv2_server.py"], stdin=logfile, stdout=logfile, stderr=logfile, shell=True)
            django_server = subprocess.Popen(["""WPy64-38100\python-3.8.10.amd64\python.exe""", "manage.py", "runserver"], stdin=logfile, stdout=logfile, stderr=logfile, shell=True)
        elif os.name == 'posix':
            cv_client = subprocess.Popen(["""venv/bin/python3""", "zmq_cv2_server.py"], stdin=logfile, stdout=logfile, stderr=logfile, shell=True)
            django_server = subprocess.Popen(["""venv/bin/python""", "manage.py", "runserver"], stdin=logfile, stdout=logfile, stderr=logfile, shell=True)
        print("Process started!")
        pool = True
        time.sleep(3)
        webbrowser.open('http://localhost:8000', new=0, autoraise=True)
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
        if os.name == 'nt':
            subprocess.Popen(shlex.split("taskkill /F /T /PID %d" % cv_client.pid), stdin=logfile, stdout=logfile, stderr=logfile, shell=True) # psutil
            subprocess.Popen(shlex.split("taskkill /F /T /PID %d" % django_server.pid), stdin=logfile, stdout=logfile, stderr=logfile, shell=True) # psutil
        elif os.name == 'posix':
            cv_client.kill()
            django_server.kill()

        print("Process killed!")
        pool = False
    else:
        print("Process is not running!")

def on_restart(icon, item):
    on_stop(icon, item)
    time.sleep(1)
    on_run(icon, item)

def on_exit(icon, item):
    on_stop(icon, item)
    icon.stop()

ic = icon(NAME, ICON, menu=menu(
    item(
        ACT_RUN,
        on_run),
    item(
        ACT_RESTART,
        on_restart),
    item(
        ACT_STOP,
        on_stop),
    item(
        ACT_EXIT,
        on_exit)))


if __name__ == '__main__':
    run_check()
    #startup_actions()
    ic.run()
    os.remove(lockfile)
