import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from tracking.tracker import Tracker


class MediaPipeTracker(Tracker):

    # The tracker class is responsible for capturing frames from the source and detecting people in the frames
    def __init__(self, source : str):
        self.source = source

        base_options = python.BaseOptions(model_asset_path="tracking/media_pipe/efficientdet_lite0.tflite")
        options = vision.ObjectDetectorOptions(base_options=base_options, score_threshold=0.5, category_allowlist=["person"])
        self.object_detector = vision.ObjectDetector.create_from_options(options)

        # Open the video source
        if self.source:
            self.cap = cv2.VideoCapture(self.source)  
        else:
            self.cap = cv2.VideoCapture(0)

    # Detect people in the frame
    def detectPerson(self, object_detector, frame, inHeight=500, inWidth=0):
        frameOpenCV = frame.copy()
        frameHeight = frameOpenCV.shape[0]
        frameWidth = frameOpenCV.shape[1]

        if not inWidth:
            inWidth = int((frameWidth / frameHeight) * inHeight)

        scaleHeight = frameHeight / inHeight
        scaleWidth = frameWidth / inWidth

        frameSmall = cv2.resize(frameOpenCV, (inWidth, inHeight))
        frameRGB = cv2.cvtColor(frameSmall, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frameRGB)
        detection_result = object_detector.detect(mp_image)
        bboxes = []
        if detection_result:
            for detection in detection_result.detections:
                #print(detection)
                bboxC = detection.bounding_box
                #print(bboxC)
                #x = int(bboxC.origin_x * inWidth)
                #y = int(bboxC.origin_y * inHeight)
                #w = int(bboxC.width * inWidth)
                #h = int(bboxC.height * inHeight)

                x1 = bboxC.origin_x
                y1 = bboxC.origin_y
                x2 = bboxC.origin_x + bboxC.width
                y2 = bboxC.origin_y + bboxC.height

                # Scale bounding box back to original frame size
                cvRect = [
                    int(x1 * scaleWidth),
                    int(y1 * scaleHeight),
                    int(x2 * scaleWidth),
                    int(y2 * scaleHeight)
                ]
                bboxes.append(cvRect)
        return bboxes
    
    # Capture a frame from the source and detect faces in the frame
    def capture_frame(self):

        hasFrame, frame = self.cap.read()
        if not hasFrame:
            return None

        bboxes = self.detectPerson(self.object_detector, frame)

        #Drawing boxes on screen this can be removed later
        
        for bbox in bboxes:
            x1, y1, x2, y2 = bbox
            # Draw the rectangle on the frame (color = green, thickness = 2)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            color = (0, 255, 0)  # Green color for the center point
            radius = 10          # Radius of the circle
            thickness = -1       # -1 fills the circle

            bbox_center_x = (x1 + x2) // 2
            bbox_center_y = (y1 + y2) // 2

            cv2.circle(frame, (bbox_center_x, bbox_center_y), radius, color, thickness)

        # Display the frame with bounding boxes in a window
        cv2.imshow('Object Detection', frame)
        

        return bboxes
