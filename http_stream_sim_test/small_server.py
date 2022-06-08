from collections import OrderedDict
from flask import Flask
from flask import request, render_template 
from flask import Response
import json, os
import time
from uuid import uuid4
import cv2
from psutil import Popen
from cam_check import CamProcessor
from threading import Lock
import subprocess
import base64
import numpy as np
from afterThisResponse import AfterThisResponse

NET = None
METADATA = None
MAX_PROCESSES = 1
num_sessions = 0

class Processor:
    def __init__(self):
        self.lock = Lock()
        self.outputImage = None
        self.process = None
        self.process_id = None
    
    def run(self, process_id):
        try:
            self.process = subprocess.Popen(['python3','cam_check.py'],stdout=subprocess.PIPE)
            self.process_id = process_id
        except Exception as e:
            print(e)
    
    def stop(self):
        self.process.terminate()

    def read_image(self):
        for line in self.process.stdout:
            with self.lock:
                #service_reader.read_image(line.rstrip() )
                jpg = base64.b64decode(line.rstrip()[2:-1])
                jpg_as_np = np.frombuffer(jpg, dtype=np.uint8)
                img = cv2.imdecode(jpg_as_np, flags=1)

                #service_reader.read_image(img)  
                self.outputImage = img


def process_running(process_list, pid):
    try:
        return True if process_list[pid] else False
    except:
        return False

#======================================================Requests============================================================
app = Flask("after_response")
AfterThisResponse(app)

# Creates the processor object and loads the detection model.
#service_reader = ProcessReader()
process_list = OrderedDict()

# Cancel request. This cancels the current process being handled.
@app.route('/cancel/<process_id>', methods=['POST'])
def cancelProcessing(process_id):
    global process_list
    assert process_id == request.view_args['process_id']

    if not process_running(process_list,process_id):
        return Response("Process is not Running")

    # Sets the cancel flag to True. tha is all needed.
    process_list[process_id].stop()
    return "cancelled"

# This service starts a video processing and increases a counter to not start more processes than it can handle.
@app.route('/start/<process_id>',methods=['POST'])            
def start(process_id):
    global process_list
    assert process_id == request.view_args['process_id']
    
    if process_running(process_list,process_id):
        return Response("Process Already running")

    print(f'Requested processing for process : {process_id}')
    process_list[process_id] = Processor()
    process_list[process_id].run(process_id)
    print(f'Started Process with Id : {process_list[process_id].process_id}')

    @app.after_this_response
    def post_process():
        if not process_running(process_list,process_id):
            return 1

        print(f'Processing {process_list[process_id].process_id}')
        process_list[process_id] = process_list[process_id].read_image()
        print(f'Finished ')
    
    return "started"

# This service generates the images that result from the video processing.
def generate(process_id):
	# grab global references to the output frame and lock variables
    global process_list
    
	# loop over frames from the output stream
    while True:
        if not process_running(process_list,process_id):
            continue

		# wait until the lock is acquired
        with process_list[process_id].lock:
			# check if the output frame is available, otherwise skip
			# the iteration of the loop
            if process_list[process_id].outputImage is None:
                continue

			# encode the frame in JPEG format
            (flag, encodedImage) = cv2.imencode(".jpg", process_list[process_id].outputImage)

			# ensure the frame was successfully encoded
            if not flag:
                continue

		# yield the output frame in the byte format
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
            bytearray(encodedImage) + b'\r\n')

# This services takes the images generated and creates a video feed.
@app.route("/video_feed/<process_id>")
def video_feed(process_id):
    global process_list
    assert process_id == request.view_args['process_id']
    if not process_running(process_list,process_id):
        return Response("404. Page not found")

	# return the response generated along with the specific media
	# type (mime type)
    return Response(generate(process_id),
		mimetype = "multipart/x-mixed-replace; boundary=frame")
#==========================================================================================================================

if __name__ == "__main__":

    print(MAX_PROCESSES, num_sessions)     
    
    app.run(host='0.0.0.0', port=6500)
