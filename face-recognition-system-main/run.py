import os
import sys
import shlex
import subprocess

import sqlite3

conn = sqlite3.connect(os.path.join('src', 'data', 'tmp.db'))
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

cv_client = subprocess.Popen([sys.executable, "socket_cv2_client.py"])
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




