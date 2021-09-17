import cv2
import imutils
import numpy as np
import time
from face_detection import FaceDetection
from scipy import signal
import sys
from numpy.linalg import inv
import dlib
import imutils
import time
import skin_detector
import face_recognition
import pickle


np.set_printoptions(threshold=sys.maxsize)


def face_detect_and_thresh(frame):
    skinM = skin_detector.process(frame)
    skin = cv2.bitwise_and(frame, frame, mask = skinM)
    cv2.imshow("skin2",skin)
    return skin,skinM


def spartialAverage(thresh,frame):
    a=list(np.argwhere(thresh>0))
    ind_img=(np.vstack((a)))
    sig_fin=np.zeros([np.shape(ind_img)[0],3])
    test_fin=[]
    for i in range(np.shape(ind_img)[0]):
        sig_temp=frame[ind_img[i,0],ind_img[i,1],:]
        sig_temp = sig_temp.reshape((1, 3))
        if sig_temp.any()!=0:
            sig_fin=np.concatenate((sig_fin,sig_temp))
    for _ in sig_fin:
        if sum(_)>0:
            test_fin.append(_)
    a= [item for item in sig_fin if sum(item)>0]
    min_value=sum(min(a, key=sum))
    max_value=sum(max(a, key=sum))
    img_rgb_mean=np.nanmean(test_fin,axis=0)
    print(img_rgb_mean)
    return img_rgb_mean,min_value,max_value

def MeanRGB(thresh,frame,last_stage,min_value,max_value):
    cv2.imshow("threshh",thresh)
    print("==<>>")
    a= [item for item in frame[0] if (sum(item)>min_value and sum(item)<max_value)]
    print(a)
    if a:
        print("==>")
        print("==>")
        img_mean=np.mean(a, axis=(0))

        return img_mean[::-1]
    else:
        return last_stage

def preprocess(z1,z2,detrended_RGB,window_size,size_video,duration,frame):
    temp=(int(size_video/duration))
    f=frame-2

    main_R=[]
    main_B=[]
    out=[]
    for i in range(len(detrended_RGB)-f+1):

        temp_R=z1[i:i+f-1]
        temp_B=z2[i:i+f-1]
        p=[list(a) for a in zip(temp_R, temp_B)]

        out.append(p)
    return out[0]


def SPooEsitmate(final_sig,video_size,frames,seconds):
    A = 100.6
    B = 4.834
    ten=10
    z1=[item[0] for item in final_sig]
    z3=[item[2] for item in final_sig]
    SPO_pre=[]
    for _ in range(len(z1)):
        SPO_pre.append([z1[_],z3[_]])
    Spo2 = preprocess(z1,z3,SPO_pre,ten,video_size,seconds,frames)

    R_temp = [item[0] for item in Spo2]
    DC_R_comp=np.mean(R_temp)
    AC_R_comp=np.std(R_temp)
    I_r=AC_R_comp/DC_R_comp

    B_temp = [item[1] for item in Spo2]
    DC_B_comp=np.mean(B_temp)
    AC_B_comp=np.std(B_temp)

    print(I_r)
    I_b=AC_B_comp/DC_B_comp
    SpO2_value=(A-B*((I_b*650)/(I_r*950)))
    return SpO2_value



vid = cv2.VideoCapture(0)

frameCount=0

duration=10

totalFrame = 250

final_sig=[]

qFlag=0

spo2_set=[]

data = pickle.loads(open("test.pickle", "rb").read())

while(True):

    # Capture the video frame
    # by frame
    ret, frame = vid.read()
    frame=imutils.resize(frame,width=400,height=400)
    # Display the resulting frame
    faceFrame = frame[100:200,150:250]
    boxes=[(100,250,200,150)]
    encodings = face_recognition.face_encodings(frame, boxes)
    name=[]
    for encoding in encodings:
        matches = face_recognition.compare_faces(data["encodings"],
        encoding)
        name = "Unkown"

        if True in matches:
            matchedIdxs = [i for (i,b) in enumerate(matches) if b]
            counts ={}

            for i in matchedIdxs:
                name = data["names"][i]
                counts[name]=counts.get(name,0)+1

            name = max(counts,key=counts.get)
        print(name)
    cv2.waitKey()
    cv2.imshow('frame', frame)
    cv2.imshow('face_frame', faceFrame)

    while(frameCount<totalFrame):
        ret, frame = vid.read()
        frame=imutils.resize(frame,width=400,height=400)
        boxFrame=frame.copy()
        cv2.rectangle(boxFrame,(150,100),(250,200),(0,0,255),3)
        faceFrame = frame[100:200,150:250]
        if frameCount==0:
            thresh,mask=face_detect_and_thresh(faceFrame)
            temp,min_value,max_value=spartialAverage(mask,faceFrame)
            final_sig.append(temp)
        else:
            thresh,mask=face_detect_and_thresh(faceFrame)

            final_sig.append(MeanRGB(thresh,faceFrame,final_sig[-1],min_value,max_value))
        frameCount=frameCount+1
        cv2.imshow('frame', boxFrame)
        cv2.imshow("face_frame",faceFrame)
        cv2.waitKey(1)
    result=SPooEsitmate(final_sig,totalFrame,totalFrame,duration) # the final signal list is sent to SPooEsitmate function with length of the video
    print(result)
    if(len(spo2_set)<10):
        spo2_set.append(result)
    else:
        print(spo2_set)
        print(np.mean(spo2_set))
    cv2.waitKey()

    frameCount=0

    duration=10

    totalFrame = 250

    final_sig=[]


    # the 'q' button is set as the
    # quitting button you may use any
    # desired button of your choice
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

# After the loop release the cap object
vid.release()
# Destroy all the windows
cv2.destroyAllWindows()
