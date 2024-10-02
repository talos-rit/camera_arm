from tracking.tracker import Tracker
import cv2

class BasicTracker(Tracker):

    # The tracker class is responsible for capturing frames from the source and detecting faces in the frames
    def __init__(self, source : str):
        self.source = source

        self.faceCascade = cv2.CascadeClassifier("tracking/haarcascade_frontalface_default.xml")

        # Open the video source
        if self.source:
            self.cap = cv2.VideoCapture(self.source)  
        else:
            self.cap = cv2.VideoCapture(0)

    # Detect faces in the frame
    def detectFace(self, faceCascade, frame, inHeight=500, inWidth=0):
        frameOpenCVHaar = frame.copy()
        frameHeight = frameOpenCVHaar.shape[0]
        frameWidth = frameOpenCVHaar.shape[1]
        if not inWidth:
            inWidth = int((frameWidth / frameHeight) * inHeight)

        scaleHeight = frameHeight / inHeight
        scaleWidth = frameWidth / inWidth

        frameOpenCVHaarSmall = cv2.resize(frameOpenCVHaar, (inWidth, inHeight))
        frameGray = cv2.cvtColor(frameOpenCVHaarSmall, cv2.COLOR_BGR2GRAY)

        faces = faceCascade.detectMultiScale(frameGray)
        bboxes = []
        for (x, y, w, h) in faces:
            x1 = x
            y1 = y
            x2 = x + w
            y2 = y + h
            cvRect = [
                int(x1 * scaleWidth),
                int(y1 * scaleHeight),
                int(x2 * scaleWidth),
                int(y2 * scaleHeight),
            ]
            bboxes.append(cvRect)
        return bboxes, frameHeight, frameWidth
    
    # Capture a frame from the source and detect faces in the frame
    def capture_frame(self):

        hasFrame, frame = self.cap.read()
        if not hasFrame:
            return None, None, None

        bboxes, frameHeight, frameWidth = self.detectFace(self.faceCascade, frame)
        
        return bboxes, frameHeight, frameWidth