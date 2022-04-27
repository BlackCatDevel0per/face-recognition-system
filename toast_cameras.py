from cv2 import VideoCapture
from pyautogui import alert

def CameraIndexes() -> list:
	index = 0
	arr = []
	iter_idx = 10

	while iter_idx > 0:
		cap = VideoCapture(index)
		if cap.read()[0]:
			arr.append(index)
			cap.release()
		index += 1
		iter_idx -= 1

	return arr

if __name__ == '__main__':
	print(CameraIndexes())
	alert(CameraIndexes(), title="CAM List")