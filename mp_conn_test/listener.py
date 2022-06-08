from multiprocessing.connection import Listener
import time
import cv2
import base64
import numpy as np

address = ('192.168.0.98', 6000)     # family is deduced to be 'AF_INET'
listener = Listener(address, authkey=b'12456')
conn = listener.accept()
print('connection accepted from', listener.last_accepted)
sent = 0
while True:
    print("iters")
    msg = conn.recv()
    # do something with msg
    #print(msg)
    if msg == 'close':
        conn.close()
        break
    else:
        jpg = base64.b64decode(msg)
        jpg_as_np = np.frombuffer(jpg, dtype=np.uint8)
        img = cv2.imdecode(jpg_as_np, flags=1)
listener.close()

cv2.imshow('decoded',img)
cv2.waitKey(0)
cv2.destroyAllWindows()
