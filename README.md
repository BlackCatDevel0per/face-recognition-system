
# face-recognition-system
Simple face recognition system

## Install requirements (Recommended in virtualenv)
```
pip install face-recognition==1.3.0 face-recognition-models==0.3.0 --no-deps
pip install -r requirements.txt
# Or simple run (only for windows):
pip install -r requirements1.txt
```

### Linux
```
pip install virtualenv
python -m virtualenv venv
source venv/bin/activate
```
### Windows
```
pip install virtualenv
python -m virtualenv venv
source venv\Scripts\activate.bat
```

# Run code!
```
# In browser go to http://127.0.0.1:8000/monitor
python run.py
```

# Settings:
Default user and password: admin, texnopark

# Planing add
- [ ] Update system, distributing and etc.
- [ ] web interface rewrite (last updated 28.04.2022)
- [ ] PostgreSQL
- [ ] Logging
- [ ] Run in PyPy (opencv)
- [X] Socket streaming
- [X] Rewrite socket to other.. (For multiuser support) - ZMQ
Other things..

# Used Code
https://github.com/ageitgey/face_recognition/

https://github.com/abhikesare9/live-streaming-with-opencv
