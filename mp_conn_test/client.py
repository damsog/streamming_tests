from multiprocessing.connection import Client
import cv2
import numpy as np
import base64


address = ('192.168.0.98', 6000)
conn = Client(address, authkey=b'12456')

img = cv2.imread('/media/pdi/Tyr/mp_test/cam.jpg')
_,buff = cv2.imencode('.jpg',img)
jpg_as_txt = base64.b64encode(buff)

conn.send(jpg_as_txt)


#conn.send('hi')
conn.send('close')
conn.close()
