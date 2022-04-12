# face-recognition-system
Simple face recognition system

## Install requirements (Recommended in virtualenv)
```
pip install face-recognition==1.3.0 face-recognition-models==0.3.0 --no-deps
pip install -r requirements.txt
# Or simple run:
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

# Planing add
- [ ] PostgreSQL
- [ ] web interface
- [ ] Update system, distributing and etc.
- [ ] Logging
- [ ] Run in PyPy (opencv)
- [X] Socket streaming
Other things..
- [ ] Rewrite socket to REST API

# Used Code
https://github.com/ageitgey/face_recognition/

https://github.com/abhikesare9/live-streaming-with-opencv
