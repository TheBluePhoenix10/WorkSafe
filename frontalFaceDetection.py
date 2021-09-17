import os

from imutils.video import VideoStream
import numpy as np
import argparse
import imutils
import time
import cv2

net = cv2.dnn.readNetFromCaffe("models/deploy.prototxt.txt", "models/res10_300x300_ssd_iter_140000.caffemodel")

def fix_box(frame):
    frameOG = frame.copy()
    (h,w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame,(300,300)),1.0,
                                    (300,300),(104.0,177.0,123.0))
    net.setInput(blob)
    detections = net.forward()
    test=[0,0,0,0,0,0,0,0,0,0,0]
    for i in test:
        confidence = detections[0,0,i,2]
        if confidence < 0.8:
            continue
        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
        (startX, startY, endX, endY) = box.astype("int")
        text = "{:.2f}%".format(confidence * 100)
        y = startY - 10 if startY - 10 > 10 else startY + 10
        startX2=int(int((endX+startX)/2)-50*1.3)
        endX2=int(int((endX+startX)/2)+50*1.3)
        startY2=int(int((endY+startY)/2)-50*1.3)
        endY2=int(int((endY+startY)/2)+50*1.3)
        
        if ( startX2>=400 ) or ( startY2>=400 ) or ( endY2>=400 ) or ( endX2>=400 ):
            raise Exception('Face out of bounds')
        cv2.rectangle(frame, (startX2, startY2), (endX2, endY2),(0, 0, 255), 2)
        
    box=[(startY2,endX2,endY2,startX2)]
    
    return frame,frameOG[startY2:endY2,startX2:endX2],box
    
def detectionFrontFace(frame):
    (h,w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame,(300,300)),1.0,
                                 (300,300),(104.0,177.0,123.0))
    net.setInput(blob)
    detections = net.forward()
    
    for i in range(0,detections.shape[2]):
        confidence = detections[0,0,i,2]
        # print(confidence)
        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
        (startX, startY, endX, endY) = box.astype("int")
        x=startX-endX
        y=startY-endY
        area= x*y
        if confidence < 0.9660:
            return 0
        else:
            return 1
    