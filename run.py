import os
import sys
import shlex
import subprocess

ldir = os.listdir(os.path.join("src", "images"))
cuuid = None
for p in ldir:
   if "___" in p and p.endswith(".jpg"):
      cuuid = p.split("___")[1].replace(".jpg", "")
      break
   else:
      print("Bad filename: ", p)

cv_client = subprocess.Popen([sys.executable, "socket_cv2_server.py"])
django_server = subprocess.Popen([sys.executable, "manage.py", "runserver"])

try:
    cv_client.wait()
    django_server.wait()
except KeyboardInterrupt:
    try:
       cv_client.terminate()
       django_server.terminate()
    except OSError:
       pass
    cv_client.wait()
    django_server.wait()
except Exception as e:
   print(e)




