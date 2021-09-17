# Copyright (c) Sachin Singh Bhadoriya 2020

import cv2
from request import getRequest, sendRequest, url_ok, upload
from password_check import checkPassword, check_Password
import uuid
import re
from frontalFaceDetection import detectionFrontFace, fix_box
from string_manipulation import stringGetValue, changeTemp
import webbrowser
import pyperclip
from encode_faces import trainModel
import threading
import os
from request import checkPing
from emailSender import send_mail
from IP_scan import get_value
from IP_scan import get_IP
from HeartRate import Process
import pickle
import face_recognition
import skin_detector
import dlib
from numpy.linalg import inv
import sys
from scipy import signal
from face_detection import FaceDetection
import time
import numpy as np
import imutils
from attendance import checkName
from datetime import date
from os import path
VERSION = "Main Window"

try:
    from PyQt5.QtCore import Qt
    pyqt5 = True
except:
    pyqt5 = False
if pyqt5:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtCore import QTimer, QPoint, pyqtSignal
    from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QLabel, QSplashScreen
    from PyQt5.QtWidgets import QWidget, QAction, QVBoxLayout, QHBoxLayout
    from PyQt5.QtGui import QFont, QPainter, QImage, QTextCursor, QPixmap
    from PyQt5 import QtCore, QtGui
else:
    from PyQt4.QtCore import Qt, pyqtSignal, QTimer, QPoint
    from PyQt4.QtGui import QApplication, QMainWindow, QTextEdit, QLabel
    from PyQt4.QtGui import QWidget, QAction, QVBoxLayout, QHBoxLayout
    from PyQt4.QtGui import QFont, QPainter, QImage, QTextCursor
try:
    import Queue as Queue
except:
    import queue as Queue

IMG_SIZE = 400, 400          # 640,480 or 1280,720 or 1920,1080
IMG_FORMAT = QImage.Format_RGB888
DISP_SCALE = 1                # Scaling factor for display image
DISP_MSEC = 50                # Delay between display cycles
CAP_API = cv2.CAP_ANY       # API: CAP_ANY or CAP_DSHOW etc...
EXPOSURE = 0                 # Zero for automatic exposure
TEXT_FONT = QFont("Courier", 10)

camera_num = 1                 # Default camera (first in list)
image_queue = Queue.Queue()     # Queue to hold images
capturing = True              # Flag to indicate capturing

setupFlag = True

NoScanFlag = False

recordFlag = False

frontalFlag = True

isRecordingFlag = False


frameCount = 0

globalCount = 0

frontFaceCount = 0

duration = 10

totalFrame = 250

Spo2Flag = 0

FaceDetectionFlag = 0

pickelName = None

final_sig = []

name = []

boxes = [(100, 250, 200, 150)]

spo2_set = []

size_ratio = []

no_of_retries = 5

data = pickle.loads(open("models/Trainedpickels/updated.pickle", "rb").read())

process = Process()
hr = 0
bpm = 0
heartRate = 0

hrSet = []

cam_ip_temp_holder = 0


def face_detect_and_thresh(frame):
    skinM = skin_detector.process(frame)
    skin = cv2.bitwise_and(frame, frame, mask=skinM)
    return skin, skinM


def spartialAverage(thresh, frame):
    a = list(np.argwhere(thresh > 0))
    if a:
        ind_img = (np.vstack((a)))
    else:
        return 0, 0, 0
    sig_fin = np.zeros([np.shape(ind_img)[0], 3])
    test_fin = []
    for i in range(np.shape(ind_img)[0]):
        sig_temp = frame[ind_img[i, 0], ind_img[i, 1], :]
        sig_temp = sig_temp.reshape((1, 3))
        if sig_temp.any() != 0:
            sig_fin = np.concatenate((sig_fin, sig_temp))
    # print(sig_fin)
    for _ in sig_fin:
        if sum(_) > 0:
            # test_fin=np.concatenate((test_fin,_))
            test_fin.append(_)
    # print("min=>")
    a = [item for item in sig_fin if sum(item) > 0]
    # print(min(a, key=sum))
    min_value = sum(min(a, key=sum))
    max_value = sum(max(a, key=sum))
    # print(sum1)
    img_rgb_mean = np.nanmean(test_fin, axis=0)
    # print(img_rgb_mean)
    return img_rgb_mean, min_value, max_value


def MeanRGB(thresh, frame, last_stage, min_value, max_value):
    # cv2.imshow("threshh",thresh)
    # print(thresh)
    # print("==<>>")
    # print(img_rgb)
    # cv2.waitKey(1)
    # print(img_rgb[0])
    # thresh=thresh.reshape((1,3))
    # img_rgb_mean=np.nanmean(thresh,axis=0)
    a = [item for item in frame[0] if (
        sum(item) > min_value and sum(item) < max_value)]
    # print(a)
    # a = filter(lambda (x,y,z) : i+j+k>764 ,frame[0])
    # print(a[1:10])
    # img_temp = [item for item in img_rgb if sum(item)>764]
    # print(frame[0])
    # print(img_temp)
    # print(np.mean(a, axis=(0)))
    if a:
        # print("==>")
        # print(a)
        # print("==>")
        img_mean = np.mean(a, axis=(0))
        # print(img_mean)

        return img_mean[::-1]
    else:
        return last_stage


def preprocess(z1, z2, detrended_RGB, window_size, size_video, duration, frame):
    temp = (int(size_video/duration))
    f = frame-2

    main_R = []
    main_B = []
    out = []
    for i in range(len(detrended_RGB)-f+1):

        temp_R = z1[i:i+f-1]
        temp_B = z2[i:i+f-1]
        p = [list(a) for a in zip(temp_R, temp_B)]

        out.append(p)
        # if not main_R:
        #     main_R.append(temp_R)
        # else:
        #     main_R=[main_R,temp_R]
        #
        # if not main_B:
        #     main_B.append(temp_B)
        # else:
        #     main_B=[main_B,temp_B]

    # out=[main_R,main_B]
    # print(out[0])
    return out[0]


def SPooEsitmate(final_sig, video_size, frames, seconds):
    A = 100.6
    B = 4.834
    ten = 10
    z1 = [item[0] for item in final_sig]
    z3 = [item[2] for item in final_sig]
    SPO_pre = []
    for _ in range(len(z1)):
        SPO_pre.append([z1[_], z3[_]])
    Spo2 = preprocess(z1, z3, SPO_pre, ten, video_size, seconds, frames)

    R_temp = [item[0] for item in Spo2]
    DC_R_comp = np.mean(R_temp)
    AC_R_comp = np.std(R_temp)
    # print(DC_R_comp)
    # print(R_temp)
    # print(AC_R_comp)
    I_r = AC_R_comp/DC_R_comp

    B_temp = [item[1] for item in Spo2]
    DC_B_comp = np.mean(B_temp)
    AC_B_comp = np.std(B_temp)

    # print(I_r)
    I_b = AC_B_comp/DC_B_comp
    SpO2_value = (A-B*((I_b*650)/(I_r*950)))
    return SpO2_value


# Grab images from the camera (separate thread)
def grab_images(cam_num, queue, self):
    global data
    global boxes
    global frameCount
    global globalCount
    global totalFrame
    global FaceDetectionFlag
    global Spo2Flag
    global bpm
    global hr
    global no_of_retries
    # global recordFlag
    global hrSet
    global frontalFlag
    global frontFaceCount
    isRecordingFlag = False
    # global autoFlag
    recordFlag = self.recordFlag
    self.captureFlag = False
    self.FailCheck = False
    bpm = 0
    hr = 0

    # cap = cv2.VideoCapture(cam_num-1 + CAP_API)
    print(type(cam_num))
    if(cam_num=="0" or cam_num=="1"): cam_num = int(cam_num)
    cap = cv2.VideoCapture(cam_num)
    # fps = cap.get(cv2.CAP_PROP_FPS)
    # cap.set(cv2.CAP_PROP_FPS, fps)
    while 1:
        if cap:
            pass
        else:
            cap.release()
            cap = cv2.VideoCapture(cam_num)
        time.sleep(2)
        if cap.grab():
            self.captureFlag = True
            break
        else:
            # if(no_of_retries > 0):
            #     no_of_retries = no_of_retries - 1
            # else:
            #     QMessageBox.information(
            #         self, "Alert", "End of Video File Reached, The program will exit now.")
            # print("waiting for capture")
            
            self.captureFlag = False

    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    size = (frame_width, frame_height)
    self.flashFlag = False
    name_final = ''
    if EXPOSURE:
        cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
        cap.set(cv2.CAP_PROP_EXPOSURE, EXPOSURE)
    else:
        cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
    while capturing:
        if cap.grab():
            self.captureFlag = True
            retval, image = cap.retrieve(0)
            image = imutils.resize(image, width=400, height=400)
            if self.RotationFlag > 0:
                image = cv2.rotate(
                    image, (self.RotationDictionary.get(self.RotationFlag)))
            fullScale = image.copy()
            recordVid = image.copy()
            fullScale = imutils.resize(fullScale, width=400, height=400)

            fullScale = cv2.cvtColor(fullScale, cv2.COLOR_BGR2RGB)

            if self.recordFlag:
                # print("made copy")
                saveFrame = fullScale.copy()

            cv2.waitKey(1)
            if (self.recordFlag) and (not isRecordingFlag):
                # print("made writer")
                today = date.today()
                t = time.localtime()
                current_time = time.strftime("%H%M%S", t)
                # print(current_time)
                if os.path.exists("recordings/"+str(today)):
                    self.recording = cv2.VideoWriter("recordings/"+str(today)+'/'+str(current_time)+'.avi',
                                                     cv2.VideoWriter_fourcc(
                                                         *'MJPG'),
                                                     20, (400, 400))
                else:
                    os.mkdir("recordings/"+str(today))
                    self.recording = cv2.VideoWriter("recordings/"+str(today)+'/'+str(
                        current_time)+'.avi', cv2.VideoWriter_fourcc(*'MJPG'), 20, (400, 400))
                isRecordingFlag = True

            image = imutils.resize(image, width=400, height=400)
            boxFrame = image.copy()
            # print(queue.qsize())
            # cv2.rectangle(boxFrame,(150,100),(250,200),(0,0,255),3)
            # faceFrame = image[100:200,150:250]
            # cv2.rectangle(boxFrame,(int(150*0.9),int(100*0.9)),(int(250*1.1),int(200*1.1)),(0,0,255),3)
            if not hasattr(self, 'lastfaceFrame'):
                self.lastfaceFrame = boxFrame[int(
                    100*0.9):int(200*1.1), int(150*0.9):int(250*1.1)]

            try:
                image, faceFrame, boxes = fix_box(image)
            except Exception as e:
                print("error",e)
                faceFrame = boxFrame[int(
                    100*0.9):int(200*1.1), int(150*0.9):int(250*1.1)]
                boxes = [(int(100*0.9), int(250*0.9),
                          int(200*0.9), int(150*0.9))]
                
                                          
            height, width, channels = faceFrame.shape

            if height > 0 and width > 0:
                self.lastfaceFrame = faceFrame

            else:
                faceFrame = self.lastfaceFrame

            # print(height, width)

            cv2.imshow("faceFrame",faceFrame)
            # print(self.autoFlag)
            if self.autoFlag:

                if frontalFlag and detectionFrontFace(faceFrame.copy()):
                    frontFaceCount = frontFaceCount+1
                    if frontFaceCount == 15:
                        frontalFlag = False
                        frontFaceCount = 0
                        self.clickme()
            # cv2.imshow("face",faceFrame)
            cv2.waitKey(1)
            if boxFrame is not None and (queue.qsize() < 2 or (Spo2Flag)):
                # faceFrame = image[100:200,150:250]
                # print(queue.qsize())

                if (FaceDetectionFlag) and frameCount < 10:
                    self.counts = {}
                    if frameCount == 0:
                        print('reset')
                        self.CheckFlag = {}

                    encodings = face_recognition.face_encodings(image, boxes)
                    for encoding in encodings:
                        matches = face_recognition.compare_faces(data["encodings"],
                                                                 encoding)
                        name = 'Unknown'

                        if True in matches:
                            matchedIdxs = [
                                i for (i, b) in enumerate(matches) if b]
                            # print(matchedIdxs)
                            # i=matchedIdxs[0]
                            # name = data["names"][i]
                            # self.counts[name]=self.counts.get(name,0)+1
                            for i in matchedIdxs:
                                name = data["names"][i]
                                self.counts[name] = self.counts.get(name, 0)+1
                            # print(self.counts)
                            try:
                                # for name in self.counts:
                                #     Tempname = name
                                #     self.CheckFlag[Tempname]=self.CheckFlag.get(Tempname,0)+1

                                Tempname = max(
                                    self.counts, key=self.counts.get)
                                # print("tempName is "+str(Tempname))
                                self.CheckFlag[Tempname] = self.CheckFlag.get(
                                    Tempname, 0)+1

                            except:
                                pass
                    # print(self.CheckFlag)

                if frameCount == 0 and (FaceDetectionFlag):

                    process = Process()
                    height = image.shape[0]
                    
                    cv2.putText(image, 'SPO2 Estimation Underway', (20, height-50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1, cv2.LINE_AA)
                    # encodings = face_recognition.face_encodings(image, boxes)

                    # for encoding in encodings:
                    #     matches = face_recognition.compare_faces(data["encodings"],
                    #     encoding)
                    #     name='Unknown'

                    #     if True in matches:
                    #         matchedIdxs = [i for (i,b) in enumerate(matches) if b]

                    #         for i in matchedIdxs:
                    #             name = data["names"][i]
                    #             self.counts[name]=self.counts.get(name,0)+1
                    #         print(self.counts)
                    #     #     name = max(counts,key=counts.get)

                    # # print(name)
                    # self.label_5.setText("Face ID:"+name)
                    # name_final=name
                    # FaceDetectionFlag=0
                    
                    thresh, mask = face_detect_and_thresh(faceFrame)

                    temp, min_value, max_value = spartialAverage(
                        mask, faceFrame)
                    # print(temp)
                    # print(type(temp))
                    # print(str(type(temp)))
                    if(type(temp) == type(2)):
                        print("failed estimation, try again")
                        frameCount = totalFrame
                        # break
                        Spo2Flag = 2

                    final_sig.append(temp)

                elif (Spo2Flag == 1) and frameCount < totalFrame and frameCount > 1:
                    height = image.shape[0]
                    cv2.putText(image, 'SPO2 Estimation', (20, height-50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                    if self.flashFlag:
                        cv2.putText(image, 'On Going', (20, height-25),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                    self.flashFlag = not self.flashFlag
                    thresh, mask = face_detect_and_thresh(faceFrame)
                    process.frame_in = boxFrame
                    try:
                        process.run()
                    except Exception as e:
                        # print(e)
                        process.bpm = self.bpmLast
                    bpm = process.bpm
                    self.bpmLast = bpm
                    if process.bpms.__len__() > 1:
                        # and bpm<100 and bpm>55):
                        if(max(process.bpms-np.mean(process.bpms)) < 200):
                            hr = np.mean(process.bpms)
                            hrSet.append(hr)
                    # if bpm>0:
                        # print(bpm)
                        # print(hr)
                    final_sig.append(
                        MeanRGB(thresh, faceFrame, final_sig[-1], min_value, max_value))
                    self.label_1.setText("Heart-Rate:"+str(int(hr)))

                if frameCount == totalFrame:

                    if Spo2Flag == 1:

                        HRavg = np.nanmean(hrSet)
                        try:
                            HRavg = int(HRavg)
                        except:
                            HRavg = 0
                        hrSet = []
                        # the final signal list is sent to SPooEsitmate function with length of the video
                        result = SPooEsitmate(
                            final_sig, totalFrame, totalFrame, duration)
                        try:
                            name = max(self.CheckFlag, key=self.CheckFlag.get)
                        except:
                            name = "Unknown"
                        # print(name)
                        self.label_5.setText("Face ID:"+name)
                        name_final = name
                        try:
                            self.label_1.setText("Heart-Rate:"+str(int(HRavg)))
                            self.label_2.setText(
                                "SPO2 Level:"+str(int(np.ceil(result))))
                        except:
                            self.label_1.setText("Heart-Rate:"+"NA")
                            self.label_2.setText("SPO2 Level:"+"NA")
                        tempFlag = 1  # checkPing(self.AI_CAN_IP)

                        if tempFlag == 1:
                            try:
                                sensorValue = get_value(self.AI_CAN_IP)
                                # print(sensorValue)
                                Ambient = stringGetValue(sensorValue, 1)
                                Ambient = changeTemp(
                                    Ambient, self.tempFormatDict, self.tempCounter)

                                Compensated = stringGetValue(sensorValue, 2)
                                Compensated = changeTemp(
                                    Compensated, self.tempFormatDict, self.tempCounter)

                                self.label_3.setText(
                                    "Ambient:"+str((format(float(Ambient), '.2f')))+" "+str(self.tempFormatDict[self.tempCounter]))
                                if Compensated > 0:
                                    self.label_4.setText(
                                        "Temp:"+str((format(float(Compensated), '.2f')))+" "+str(self.tempFormatDict[self.tempCounter]))
                                Ambient = format(float(Ambient), '.2f')
                                Compensated = format(float(Compensated), '.2f')
                                if(int(float(Compensated)) > 37 or int(HRavg) > 100 or int(np.ceil(result) < 90)):
                                    # save pic here and save
                                    # cv2.imwrite("email_content/"+str(name)+'.jpg',faceFrame)
                                    send_mail(self.email, str(name), str(np.ceil(result)), str(
                                        HRavg), str(format(float(Compensated), '.2f')))
                                    print("email alert sent")
                                    # os.remove("email_content/"+str(name)+'.jpg')
                            except:
                                Ambient = "NA"
                                Compensated = "NA"
                                self.label_3.setText(
                                    "Ambient:"+Ambient+" "+str(self.tempFormatDict[self.tempCounter]))
                                self.label_4.setText(
                                    "B.Temp:"+Compensated+" "+str(self.tempFormatDict[self.tempCounter]))

                        else:
                            Ambient = "NA"
                            Compensated = "NA"
                            self.label_3.setText(
                                "Ambient:"+Ambient+" "+str(self.tempFormatDict[self.tempCounter]))
                            self.label_4.setText(
                                "B.Temp:"+Compensated+" "+str(self.tempFormatDict[self.tempCounter]))
                            if(int(HRavg) > 100 or int(np.ceil(result) < 90)):
                                # save pic here and save
                                # cv2.imwrite("email_content/"+str(name)+'.jpg',faceFrame)
                                send_mail(self.email, str(name), str(
                                    np.ceil(result)), str(HRavg), str(Compensated))
                                print('email sent')
                                # os.remove("email_content/"+str(name)+'.jpg')

                        checkName(name_final, result, HRavg,
                                  Compensated, Ambient)

                        Spo2Flag = 0
                        FaceDetectionFlag = 0
                        # Webspo2Flag= not Webspo2Flag

                    elif Spo2Flag == 2:
                        print("Try again with face properly aligned")
                        if self.autoFlag:
                            frontalFlag = True
                        Spo2Flag = 0

                # print(self.AI_CAM_IP)
                if Spo2Flag != 2:
                    queue.put(image)

                if self.recordFlag and isRecordingFlag:
                    # print('writen')
                    cv2.putText(
                        image, 'rec:', (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1, cv2.LINE_AA)
                    recordVid = cv2.resize(recordVid, (400, 400))
                    self.recording.write(recordVid)

                if self.doneRecording:
                    if self.recordFlag:
                        self.recording.release()
                        self.recordFlag = False
                        isRecordingFlag = False
                        self.doneRecording = False

                frameCount = frameCount+1
                globalCount = globalCount + 1

                # print(globalCount)
                if globalCount % 500 == 0:
                    frontalFlag = True

                if globalCount % 500 == 0:
                    # tempFlag=checkPing(self.AI_CAN_IP)
                    tempFlag = 1
                    # print(tempFlag)
                    if (tempFlag == 1 and Spo2Flag == 0):
                        try:
                            sensorValue = get_value(self.AI_CAN_IP)
                            Ambient = stringGetValue(sensorValue, 1)
                            Ambient = changeTemp(
                                Ambient, self.tempFormatDict, self.tempCounter)

                            Compensated = stringGetValue(sensorValue, 2)
                            Compensated = changeTemp(
                                Compensated, self.tempFormatDict, self.tempCounter)

                            self.label_3.setText(
                                "Ambient:"+str((format(float(Ambient), '.2f')))+" "+str(self.tempFormatDict[self.tempCounter]))
                            if Compensated > 0:
                                self.label_4.setText(
                                    "B.Temp:"+str((format(float(Compensated), '.2f')))+" "+str(self.tempFormatDict[self.tempCounter]))
                            # if((float(Compensated))>37.7):
                            #     send_mail()
                        except:
                            Ambient = "NA"
                            Compensated = "NA"
                            self.label_3.setText(
                                "Ambient:"+Ambient+" "+str(self.tempFormatDict[self.tempCounter]))
                            self.label_4.setText(
                                "B.Temp:"+Compensated+" "+str(self.tempFormatDict[self.tempCounter]))

                    elif Spo2Flag == 0:
                        Ambient = "NA"
                        Compensated = "NA"
                        self.label_3.setText(
                            "Ambient:"+Ambient+" "+str(self.tempFormatDict[self.tempCounter]))
                        self.label_4.setText(
                            "B.Temp:"+Compensated+" "+str(self.tempFormatDict[self.tempCounter]))

                    if globalCount > 100000:
                        globalCount = 0

                # print(frameCount)
            else:
                time.sleep(DISP_MSEC / 1000.0)
        else:
            print("Error: can't grab camera image")
            self.captureFlag = False
            time.sleep(2)
            while 1:
                cap.release()
                cap = cv2.VideoCapture(cam_num)
                if cap.grab():
                    break
                else:
                    time.sleep(2)
                    print("waiting for capture")

            # break
    cap.release()


def check_url(url):
    if url == "0":
        camera = 0
    elif url == "1":
        camera = 1
    elif url == "-1":
        camera = -1
    else:
        camera = "http://"+str(url)+"/mjpeg/1"
    return camera

# Image widget


class ImageWidget(QWidget):
    def __init__(self, parent=None):
        super(ImageWidget, self).__init__(parent)
        self.image = None

    def setImage(self, image):
        self.image = image
        self.setMinimumSize(image.size())
        self.update()

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        if self.image:
            qp.drawImage(QPoint(0, 0), self.image)
        qp.end()

# Main window


class MyWindow(QMainWindow):

    text_update = pyqtSignal(str)
    # Create main window

    def __init__(self, IP, AI_CAN_IP, email, identifier, parent=None):

        QMainWindow.__init__(self, parent)

        self.central = QWidget(self)

        # Ipaddress,done1 = QInputDialog.getText(
        #      self, 'Input Dialog', 'IP address:')
        self.AI_CAN_IP = AI_CAN_IP

        self.IP = IP
        self.textbox = QTextEdit(self.central)
        self.textbox.setFont(TEXT_FONT)

        self.text_update.connect(self.append_text)
        sys.stdout = self
        global size_ratio
        self.size_ratio = size_ratio
        self.textbox.setMaximumSize(1850*size_ratio[0], 250*size_ratio[1])
        self.textbox.setMinimumSize(300*size_ratio[0], 100*size_ratio[1])
        print(size_ratio)
        print(identifier)
        print(IP)
        print(email)
        print("Camera number %u" % camera_num)
        print("Image size %u x %u" % IMG_SIZE)
        if DISP_SCALE > 1:
            print("Display scale %u:1" % DISP_SCALE)
        self.email = email
        self.vlayout = QVBoxLayout()        # Window layout
        self.displays = QHBoxLayout()
        self.disp = ImageWidget(self)
        self.displays.addWidget(self.disp)
        self.vlayout.addLayout(self.displays)
        self.label = QLabel(self)
        self.vlayout.addWidget(self.label)
        self.vlayout.addWidget(self.textbox)
        self.central.setLayout(self.vlayout)
        self.setCentralWidget(self.central)
        self.title = 'Main Window'
        self.left = 640
        self.top = 360
        self.tempFormatDict = {0: 'Celsius', 1: 'Fahrenheit', 2: 'Kelvin'}
        self.tempCounter = 0

        # self.left = 500
        # self.top = 500
        self.width = 1024
        self.height = 768
        self.autoFlag = False
        self.recordFlag = False
        self.doneRecording = False
        self.UiComponents()
        self.mainMenu = self.menuBar()      # Menu bar
        exitAction = QAction('&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(self.close)
        self.fileMenu = self.mainMenu.addMenu('&File')
        self.fileMenu.addAction(exitAction)
        self.RotationDictionary = {0: 0, 1: cv2.ROTATE_90_CLOCKWISE,
                                   2: cv2.ROTATE_180, 3: cv2.ROTATE_90_COUNTERCLOCKWISE}

        self.RotationFlag = 0

    def UiComponents(self):

        global hr

        oImage = QImage("resources/wallpaper3.png")

        sImage = oImage.scaled(QSize(1920*size_ratio[0], 1080*size_ratio[1]))

        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(sImage))

        self.setPalette(palette)

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.label_2 = QLabel('SPO2 Level:', self)
        self.label_2.move(1100*size_ratio[0], 50*size_ratio[1])
        self.label_2.resize(300*size_ratio[0], 60*size_ratio[1])
        self.label_2.setFont(QFont('Arial', 13, weight=QtGui.QFont.Bold))
        self.label_2.setStyleSheet(
            "background-color: white; border: 1px solid black;")

        self.label_1 = QLabel('Heart-Rate:', self)
        self.label_1.move(1100*size_ratio[0], 250*size_ratio[1])
        self.label_1.resize(300*size_ratio[0], 60*size_ratio[1])
        self.label_1.setFont(QFont('Arial', 13, weight=QtGui.QFont.Bold))
        self.label_1.setStyleSheet(
            "background-color: white; border: 1px solid black;")

        # Ambient body-temp face-id
        self.label_3 = QLabel('Ambient:', self)
        self.label_3.move(1550*size_ratio[0], 50*size_ratio[1])
        self.label_3.setFont(QFont('Arial', 13, weight=QtGui.QFont.Bold))
        self.label_3.resize(300*size_ratio[0], 60*size_ratio[1])
        self.label_3.setStyleSheet(
            "background-color: white; border: 1px solid black;")

        self.label_4 = QLabel('B.Temp:', self)
        self.label_4.move(1550*size_ratio[0], 250*size_ratio[1])
        self.label_4.setFont(QFont('Arial', 13, weight=QtGui.QFont.Bold))
        self.label_4.resize(300*size_ratio[0], 60*size_ratio[1])
        self.label_4.setStyleSheet(
            "background-color: white; border: 1px solid black;")

        self.label_5 = QLabel('Face ID:', self)
        self.label_5.setFont(QFont('Arial', 13, weight=QFont.Bold))
        self.label_5.move(1350*size_ratio[0], 150*size_ratio[1])
        self.label_5.resize(300*size_ratio[0], 60*size_ratio[1])
        # self.label_5.resize(200,20)
        self.label_5.setStyleSheet(
            "background-color: white; border: 1px solid black;")

        # creating a push button
        self.button = QPushButton("SPO2", self)

        # setting geometry of button
        self.button.setGeometry(200, 150, 100, 30)
        self.button.move(1600*size_ratio[0], 600*size_ratio[1])
        self.button.resize(250*size_ratio[0], 50*size_ratio[1])
        self.button.setFont(QFont('Arial', 13, weight=QFont.Bold))
        # adding action to a button

        self.button.clicked.connect(self.clickme)

        self.button2 = QPushButton("TEMPERATURE", self)

        # setting geometry of button
        self.button2.setGeometry(200, 150, 100, 30)
        self.button2.move(1600*size_ratio[0], 500*size_ratio[1])
        self.button2.setFont(QFont('Arial', 13, weight=QFont.Bold))
        self.button2.resize(250*size_ratio[0], 50*size_ratio[1])
        # adding action to a button
        self.button2.clicked.connect(self.updateV)
        # button2.move(425,335)

        self.button3 = QPushButton("RECORD", self)

        self.button3.setCheckable(True)

        # setting geometry of button
        self.button3.setGeometry(200, 150, 100, 30)
        self.button3.move(1100*size_ratio[0], 500*size_ratio[1])
        self.button3.setFont(QFont('Arial', 13, weight=QFont.Bold))
        self.button3.resize(250*size_ratio[0], 50*size_ratio[1])
        self.button3.setIcon(QIcon('resources/record_icon.jpg'))
        # adding action to a button
        self.button3.clicked.connect(self.record)

        self.button4 = QPushButton("AUTO", self)

        self.button4.setCheckable(True)

        # setting geometry of button
        self.button4.setGeometry(200, 150, 100, 30)
        self.button4.move(1350*size_ratio[0], 500*size_ratio[1])
        self.button4.setFont(QFont('Arial', 13, weight=QFont.Bold))
        self.button4.resize(250*size_ratio[0], 50*size_ratio[1])
        # adding action to a button
        self.button4.clicked.connect(self.auto)

        self.button5 = QPushButton("ROTATE", self)

        # setting geometry of button
        self.button5.setGeometry(200, 150, 100, 30)
        self.button5.move(1100*size_ratio[0], 600*size_ratio[1])
        self.button5.setFont(QFont('Arial', 13, weight=QFont.Bold))
        self.button5.resize(250*size_ratio[0], 50*size_ratio[1])
        # self.button5.move(425*3,300)

        # setting radius and border
        self.button5.setIcon(QIcon('resources/rotate_sign.png'))

        # adding action to a button
        self.button5.clicked.connect(self.rotate)

        self.button6 = QPushButton("C/F/K Shift", self)
        # setting geometry of button
        self.button6.setGeometry(200, 150, 100, 30)
        self.button6.move(1350*size_ratio[0], 600*size_ratio[1])
        self.button6.setFont(QFont('Arial', 13, weight=QFont.Bold))
        self.button6.resize(250*size_ratio[0], 50*size_ratio[1])
        # self.button5.move(425*3,300)

        # setting radius and border
        # self.button5.setIcon(QIcon('resources/rotate_sign.png'))

        # adding action to a button
        self.button6.clicked.connect(self.changeTemp)

        self.showMaximized()
        # self.show()

    def changeTemp(self):
        if self.tempCounter < 2:
            self.tempCounter = self.tempCounter + 1
        else:
            self.tempCounter = 0

    def rotate(self):
        if self.RotationFlag < 3:
            self.RotationFlag = self.RotationFlag+1
        else:
            self.RotationFlag = 0

    def auto(self):
        print("auto")
        if self.button4.isChecked():
            self.autoFlag = True
        else:
            self.autoFlag = False

    def updateV(self):
        tempFlag = 1
        print(tempFlag)
        try:

            sensorValue = get_value(self.AI_CAN_IP)
            Ambient = stringGetValue(sensorValue, 1)
            Ambient = changeTemp(
                Ambient, self.tempFormatDict, self.tempCounter)
            Compensated = stringGetValue(sensorValue, 2)
            Compensated = changeTemp(
                Compensated, self.tempFormatDict, self.tempCounter)
            self.label_3.setText(
                "Ambient:"+str((format(float(Ambient), '.2f')))+str(self.tempFormatDict[self.tempCounter]))
            if Compensated > 0:
                self.label_4.setText(
                    "B.Temp:"+str((format(float(Compensated), '.2f')))+str(self.tempFormatDict[self.tempCounter]))
            # if(int(float(Compensated))>37):
            #     send_mail()
        # if globalCount>100000:
            #     globalCount=0

            # if(int(float(Compensated))>37):
            #     send_mail()

        except:
            Ambient = "NA"
            Compensated = "NA"
            self.label_3.setText("Ambient:"+Ambient+" " +
                                 str(self.tempFormatDict[self.tempCounter]))
            self.label_4.setText("B.Temp:"+Compensated +
                                 " "+str(self.tempFormatDict[self.tempCounter]))

    def record(self):
        if self.button3.isChecked():
            print("start recording")
            self.recordFlag = True
        else:
            if self.recordFlag == True:
                self.doneRecording = True
                # recordFlag = False

    def clickme(self):
        global hr, Spo2Flag, FaceDetectionFlag, frameCount, final_sig, spo2_set, name
        final_sig = []
        name = []
        spo2_set = []
        frameCount = 0
        Spo2Flag = 1
        FaceDetectionFlag = 1
        # Ambient body-temp face-id
        self.label_2.setText("SPO2:" + " ")
        self.label_1.setText("Heart-Rate:" + " ")
        self.label_3.setText("Ambient:" + " ")
        self.label_4.setText("B.Temp:" + " ")
        self.label_5.setText("Face-ID:" + " ")
        # printing pressed
        print("pressed")

    # Start image capture & display
    def start(self):
        IP = self.IP

        print(IP)
        self.timer = QTimer(self)
        # Timer to trigger display
        self.timer.setTimerType(Qt.PreciseTimer)
        self.timer.timeout.connect(lambda:
                                   self.show_image(image_queue, self.disp, DISP_SCALE))
        self.timer.start(DISP_MSEC)
        self.capture_thread = threading.Thread(target=grab_images,
                                               args=(IP, image_queue, self))
        self.capture_thread.start()         # Thread to grab images

    # Fetch camera image from queue, and display it
    def show_image(self, imageq, display, scale):
        if not imageq.empty():
            image = imageq.get()
            if image is not None and len(image) > 0:
                img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                img = imutils.resize(img, width=int(
                    1024*self.size_ratio[0]), height=int(720*self.size_ratio[1]))
                self.display_image(img, display, scale)

    # Display an image, reduce size if required
    def display_image(self, img, display, scale=1):
        disp_size = img.shape[1]//scale, img.shape[0]//scale
        disp_bpl = disp_size[0] * 3
        if scale > 1:
            img = cv2.resize(img, disp_size,
                             interpolation=cv2.INTER_CUBIC)
        qimg = QImage(img.data, disp_size[0], disp_size[1],
                      disp_bpl, IMG_FORMAT)
        display.setImage(qimg)

    # Handle sys.stdout.write: update text display
    def write(self, text):
        self.text_update.emit(str(text))

    def flush(self):
        pass

    # Append to text display
    def append_text(self, text):
        cur = self.textbox.textCursor()     # Move cursor to end of text
        cur.movePosition(QTextCursor.End)
        s = str(text)
        while s:
            head, sep, s = s.partition("\n")  # Split line at LF
            cur.insertText(head)            # Insert text at cursor
            if sep:                         # New line if LF
                cur.insertBlock()
        self.textbox.setTextCursor(cur)     # Update visible cursor

    # Window is closing: stop video capture
    def closeEvent(self, event):
        global capturing
        capturing = False
        self.capture_thread.join()


class Window(QDialog):

    # constructor
    def __init__(self):
        super(Window, self).__init__()

        # setting window title
        self.setWindowTitle("Setup Window")

        # setting geometry to the window
        self.setGeometry(100, 100, 300, 400)

        # creating a group box
        self.formGroupBox = QGroupBox("Enter user details")

        # creating spin box to select age

        # creating a line edit
        self.nameLineEdit = QLineEdit()

        # creating a line edit
        self.emailLineEdit = QLineEdit()

        # creating a line edit
        self.iPLineEdit = QLineEdit()

        self.JsonIP = QLineEdit()

        # self.statusLabel = QLabel('')

        # calling the method that create the form
        self.createForm()

        self.NoScanButton = QPushButton(self.tr("&Proceed"))

        # creating a dialog button for ok and cancel
        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        # self.ScanButton = QPushButton('Scan')
        self.button2 = QPushButton("Register", self)

        # setting geometry of button
        self.button2.setGeometry(200, 150, 100, 30)
        # layout.addWidget(self.button2, 1, 1)

        # adding action to a button
        self.button2.clicked.connect(self.openWebsite)
        # self.CancelButton = QPushButton('Cancel')

        # self.trainModel = QPushButton('Face Recog.')

        self.hbox = QHBoxLayout()
        self.hbox.addStretch(0)
        # self.hbox.setSpacing(100)
        # self.hbox.addWidget(self.CancelButton)

        # adding action when form is accepted
        # self.ScanButton.clicked.connect(self.getInfo)

        # self.trainModel.clicked.connect(self.startTraining)

        # addding action when form is rejected
        # self.CancelButton.clicked.connect(self.reject)

        self.NoScanButton.clicked.connect(self.NoScan)

        # creating a vertical layout
        mainLayout = QVBoxLayout()

        # adding form group box to the layout
        mainLayout.addWidget(self.formGroupBox)

        # adding button box to the layout
        mainLayout.addLayout(self.hbox)

        mainLayout.addWidget(self.NoScanButton)

        mainLayout.addWidget(self.button2)

        # setting lay out
        self.setLayout(mainLayout)

    def openWebsite(self):
        webbrowser.open('https://worksafe.herokuapp.com/')
        QMessageBox.information(
            self, "Alert", "Check your browser for registration! ")

    # def startTraining(self):

    #     self.statusLabel.setText("Please wait...")
    #     time.sleep(2.0)
    #     time.sleep(3.0)
    #     checkFlag=trainModel()
    #     if checkFlag == 1:
    #         self.statusLabel.setText("Training completed")
    #     else:
    #         self.statusLabel.setText("Training failed, try again")

    def NoScan(self):
        # self.statusLabel.setText("No Scan initalization")
        print("Identifier : {0}".format(self.nameLineEdit.text()))
        print("Email : {0}".format(self.emailLineEdit.text()))
        print("IP : {0}".format(self.iPLineEdit.text()))
        Identifier = self.nameLineEdit.text()
        Email = self.emailLineEdit.text()
        self.Email = Email
        IP = check_url(self.iPLineEdit.text())
        AI_CAN_IP = "http://"+self.JsonIP.text()
        print(AI_CAN_IP)
        userDetails = {"Identifier": Identifier,
                       "Email": Email, "IP": IP, "AI_CAN_IP": AI_CAN_IP}
        with open('saved_devices/'+str(Identifier)+'.pickle', 'wb') as f:
            pickle.dump(userDetails, f)
        # closing the window

        self.getText()
        self.close()
        win = MyWindow(IP, AI_CAN_IP, Email, Identifier)
        win.show()
        win.setWindowTitle(VERSION)
        win.start()

    def getText(self):
        count = 0

        if path.exists("password/password.p"):
            text, okPressed = pickle.load(open("password/password.p", "rb"))

        while(1):
            if (("text" in locals()) and count > 1):
                if path.exists("password/password.p"):
                    os.remove("password/password.p")

            if not (("text" in locals())):
                text, okPressed = QInputDialog.getText(
                    self, "Activation Key", "Enter Activation Key:", QLineEdit.Normal, "")

            if okPressed and text != '':
                state, days_remaining = check_Password(text, self.Email)
                print(state)
                if state == 1:
                    QMessageBox.information(
                        self, "Alert", "Days remaining "+str(days_remaining))
                    pickle.dump([text, okPressed], open(
                        "password/password.p", "wb"))
                    break
                elif state == 2:
                    QMessageBox.warning(
                        self, "Error", "Kindly renew your subscription")
                    sys.exit()
                elif state == 3:
                    QMessageBox.warning(
                        self, "Error", "MAC ID has not been registered")
                    MAC = str(
                        ':'.join(re.findall('..', '%012x' % uuid.getnode())))
                    QMessageBox.information(
                        self, "Alert", "The MAC ID of your Computer is :"+MAC)
                    sys.exit()
                elif state == 4:
                    QMessageBox.warning(
                        self, "Error", "Your email address is not registered")
                    sys.exit()
                else:
                    count = count+1
                    # print(count)
                    if(count > 2):
                        sys.exit()
                    continue

    # creat form method
    def createForm(self):

        # creating a form layout
        layout = QFormLayout()

        # adding rows
        # for name and adding input text
        layout.addRow(QLabel("Identifier"), self.nameLineEdit)

        # for degree and adding combo box
        layout.addRow(QLabel("Email"), self.emailLineEdit)

        # for age and adding spin box
        layout.addRow(QLabel("Cam-IP"), self.iPLineEdit)

        layout.addRow(QLabel("Json-IP"), self.JsonIP)

        # layout.addRow(QLabel("Status:"),self.statusLabel)

        # setting layout
        self.formGroupBox.setLayout(layout)


class ListWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # setting title
        self.setWindowTitle("Selection Window")

        # setting geometry
        self.setGeometry(100, 100, 350, 450)

        # calling method
        self.UiComponents()

        # showing all the widgets
        self.show()

    # method for widgets
    def UiComponents(self):

        self.l1 = QLabel('Please select your camera from the list below', self)
        self.l1.move(50, 100)
        self.l1.adjustSize()
        self.l1.setAlignment(QtCore.Qt.AlignCenter)
        # creating a combo box widget
        self.combo_box = QComboBox(self)

        for file in os.listdir("saved_devices/"):
            if file.endswith(".pickle"):
                self.combo_box.addItem(file.split('.')[0])

        self.combo_box.move(115, 200)

        self.button = QPushButton('Select Cam', self)

        self.button.clicked.connect(self.pushed)

        self.button.move(115, 250)

        # adding items to combo box

    def pushed(self):
        global pickelName
        pickelName = str(self.combo_box.currentText())
        self.pickelName = pickelName
        self.getText()
        self.close()

    def getText(self):
        count = 0

        with open('saved_devices/'+str(pickelName)+'.pickle', 'rb') as f:
            userDetails = pickle.load(f)
            Email = userDetails.get('Email')
            f.close()

        if path.exists("password/password.p"):
            text, okPressed = pickle.load(open("password/password.p", "rb"))

        while(1):

            if (("text" in locals()) and count > 1):
                if path.exists("password/password.p"):
                    os.remove("password/password.p")

            if not (("text" in locals())):
                text, okPressed = QInputDialog.getText(
                    self, "Password", "Enter Activation Key:", QLineEdit.Normal, "")
            if okPressed and text != '':
                state, days_remaining = check_Password(text, Email)
                if state == 1:
                    QMessageBox.information(
                        self, "Alert", "Days remaining "+str(days_remaining))
                    pickle.dump([text, okPressed], open(
                        "password/password.p", "wb"))
                    break
                elif state == 2:
                    QMessageBox.warning(
                        self, "Error", "Kindly renew your subscription")
                    if path.exists("password/password.p"):
                        os.remove("password/password.p")
                    sys.exit()
                elif state == 3:
                    QMessageBox.warning(
                        self, "Error", "MAC ID has not registered")
                    MAC = str(
                        ':'.join(re.findall('..', '%012x' % uuid.getnode())))
                    QMessageBox.information(
                        self, "Alert", "The MAC ID of your Computer is :"+MAC)
                    if path.exists("password/password.p"):
                        os.remove("password/password.p")
                    sys.exit()
                elif state == 4:
                    QMessageBox.warning(
                        self, "Error", "Your email address is not registered")
                    if path.exists("password/password.p"):
                        os.remove("password/password.p")
                    sys.exit()
                else:
                    QMessageBox.warning(
                        self, "Error", "The password entered was incorrect")

                    count = count+1
                    # print(count)
                    if(count > 2):
                        sys.exit()
                    continue


# class ConfirmIP(QWidget):
#     def __init__(self):
       
#         QWidget.__init__(self)
#         layout = QGridLayout()
#         self.layout = layout
#         self.setLayout(layout)
#         self.setWindowTitle("Confirm IP or Video")
#         self.setGeometry(100, 100, 400, 400)
#         self.enterIp = QLineEdit()
#         layout.addWidget(self.enterIp)
#         self.submitButton = QPushButton("Submit")
#         layout.addWidget(self.submitButton)
#         self.submitButton.clicked.connect(self.onClicked)
#         self.show()

#     def onClicked(self):
#         global cam_ip_temp_holder
#         cam_ip_temp_holder = self.enterIp.text()
#         self.close()
#         return 0


class SetupWindow(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        MAC = (':'.join(re.findall('..', '%012x' % uuid.getnode())))
        pyperclip.copy(str(MAC))
        QMessageBox.information(
            self, "Alert", "Your MAC address is : "+str(MAC) + " This has been copied!")
        layout = QGridLayout()
        self.setLayout(layout)
        self.setWindowTitle("Setup Window")

        self.radiobuttonSetup = QRadioButton("Setup")
        self.radiobuttonSetup.setChecked(True)
        self.radiobuttonSetup.state = "Setup"

        layout.addWidget(self.radiobuttonSetup, 0, 0)

        self.radiobuttonRun = QRadioButton("Run")
        self.radiobuttonRun.state = "Run"

        layout.addWidget(self.radiobuttonRun, 0, 1)

        button = QPushButton("Proceed", self)

        # setting geometry of button
        button.setGeometry(200, 150, 100, 30)
        layout.addWidget(button, 1, 0)

        # adding action to a button
        button.clicked.connect(self.onClicked)

    def openWebsite(self):
        print("hello")

    def onClicked(self):
        global setupFlag
        if self.radiobuttonRun.isChecked():
            # self.getText()
            setupFlag = False
        else:
            setupFlag = True
        self.close()

    def getText(self):
        count = 0
        while(1):
            text, okPressed = QInputDialog.getText(
                self, "Password", "Enter Activation Key:", QLineEdit.Normal, "")
            if okPressed and text != '':
                state, days_remaining = check_Password(text)
                if state == 1:
                    QMessageBox.information(
                        self, "Alert", "Days remaining "+str(days_remaining))
                    break
                elif state == 2:
                    QMessageBox.warning(
                        self, "Error", "Kindly renew your subscription")
                    sys.exit()
                elif state == 3:
                    QMessageBox.warning(
                        self, "Error", "MAC ID has not registered")
                    MAC = str(
                        ':'.join(re.findall('..', '%012x' % uuid.getnode())))
                    QMessageBox.information(
                        self, "Alert", "The MAC ID of your Computer is :"+MAC)
                    sys.exit()
                else:
                    count = count+1
                    # print(count)
                    if(count > 2):
                        sys.exit()
                    continue


if __name__ == '__main__':
    try:
        state = QApplication(sys.argv)
        screen = SetupWindow()
        screen.show()
        state.exec()

        # path.exists("saved_devices/userData.pickle") and
        if (not setupFlag):

            PreApp = QApplication(sys.argv)
            # create the instance of our Window
            window = ListWindow()

            # start the app
            PreApp.exec()
            app = QApplication(sys.argv)

            screen = app.primaryScreen()
            size = screen.size()
            rect = screen.availableGeometry()
            width = rect.width()
            height = rect.height()
            # print(width,height)
            # global size_ratio
            size_ratio = [width/1920, height/1030]
            # print(size_ratio)
            # global pickelName
            print(pickelName)
            with open('saved_devices/'+str(pickelName)+'.pickle', 'rb') as f:
# ./recordings/2021-08-31/183911.avi
                userDetails = pickle.load(f)
                # Check IP for cam or video
                #confirmApp = QApplication(sys.argv)
                # create the instance of our Window
                #window = ConfirmIP()
                # start the app
                #confirmApp.exec()
                
                #userDetails = pickle.load(f)
                IP = userDetails.get('IP')
                #IP = cam_ip_temp_holder # userDetails.get('IP')
                print("IP is ",IP)
                
                Email = userDetails.get('Email')
                Identifier = userDetails.get("Identifier")
                AI_CAN_IP = userDetails.get("AI_CAN_IP")
                win = MyWindow(IP, AI_CAN_IP, Email, Identifier)
                win.show()
                win.setWindowTitle(VERSION)
                win.start()
                sys.exit(app.exec())

        else:
            app = QApplication(sys.argv)
            screen = app.primaryScreen()
            size = screen.size()
            rect = screen.availableGeometry()
            width = rect.width()
            height = rect.height()
            # print(width,height)
            # global size_ratio
            size_ratio = [width/1920, height/1030]
            print(size_ratio)
            window = Window()
            window.show()
            sys.exit(app.exec())
    except FileNotFoundError:
        sys.exit()

# EOF
