import sys
import cv2
from threading import Lock
import numpy as np
import base64


class CamProcessor:
  def __init__(self) -> None:
    self.status = 0
    self.outputImage = None
    self.lock = Lock()

  def run(self):
    # Create a VideoCapture object and read from input file
    # If the input is the camera, pass 0 instead of the video file name
    cap = cv2.VideoCapture(0)

    # Check if camera opened successfully
    if (cap.isOpened()== False): 
      sys.exit(1)
    # Read until video is completed
    while(cap.isOpened()):
      # Capture frame-by-frame
      ret, frame = cap.read()
      if ret == True:
        
        # perform edge detection
        img = cv2.cvtColor(cv2.Canny(frame, 100, 200), cv2.COLOR_GRAY2BGR)

        #with self.lock:
        #    self.outputImage = img.copy()


        # Display the resulting frame
        #cv2.imshow('Frame',img)
        (flag, encodedImage) = cv2.imencode(".jpg", img)
        jpg_as_txt = base64.b64encode(encodedImage)
        print(jpg_as_txt)

        # Press Q on keyboard to  exit
        if cv2.waitKey(25) & 0xFF == ord('q'):
          break

      # Break the loop
      else: 
        break

    # When everything done, release the video capture object
    cap.release()

    # Closes all the frames
    cv2.destroyAllWindows()

def main():
  cam_processor = CamProcessor()
  cam_processor.run()


if __name__ == "__main__":
  main()