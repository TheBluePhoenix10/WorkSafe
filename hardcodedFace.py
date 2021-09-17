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


frameCount=1
final_sig=[]
global gMask
global gBox
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
    a= [item for item in frame[0] if (sum(item)>200 and sum(item)<700)]
    print(a)
    if a:
        print("==>")
        print("==>")
        img_mean=np.mean(a, axis=(0))
        return img_mean[::-1]
    else:
        return last_stage

def face_detect_and_thresh2(frame):
    lower = np.array([0, 48, 80], dtype = "uint8")
    upper = np.array([20, 255, 255], dtype = "uint8")
    face_frame=frame[gBox[0]:gBox[1],gBox[2]:gBox[3]]
    frame=face_frame
    cv2.imshow("testing",frame)
    converted = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    skinMask = cv2.inRange(converted, lower, upper)
    # apply a series of erosions and dilations to the mask
    # using an elliptical kernel
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
    skinMask = cv2.erode(skinMask, kernel, iterations = 2)
    skinMask = cv2.dilate(skinMask, kernel, iterations = 2)
    # blur the mask to help remove noise, then apply the
    # mask to the frame
    skinMask = cv2.GaussianBlur(skinMask, (3, 3), 0)
    skin = cv2.bitwise_and(frame, frame, mask = skinMask)
    skin = skin_detector.process(face_frame)
    skin = cv2.bitwise_and(face_frame, face_frame, mask = skin)
    cv2.imshow("skin",skin)
    # print(np.mean(skin, axis=(0, 1)
    return skin,frame

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

cap=cv2.VideoCapture("face_video/98_6.avi") #Enter the path of video you wanna give into the code

length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) #Calculates the total number of frames present in the video
fps = cap.get(cv2.CAP_PROP_FPS)      # OpenCV2 version 2 used "CV_CAP_PROP_FPS"
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
duration = frame_count/fps
seconds = duration%60

print(length)

if (cap.isOpened()==False):
    print("Error opening video file") #Catching anykind of error while opening video

while(cap.isOpened()):
    ret,frame = cap.read()

    if frameCount==1:
        frame = imutils.resize(frame,width=400)
        cv2.imshow("testing if flipped",frame)  #just run this if you have issue with inverted frames, can result in fail detection
        cv2.waitKey()
        cv2.imshow("testing if flipped",frame)  #just run this if you have issue with inverted frames, can result in fail detection
        cv2.waitKey()

        firstFrame=frame
        thresh,maskT=face_detect_and_thresh(firstFrame) #The first frame is sent to the fuction to make a face mask
        cv2.imshow("img_rgb",thresh)
        cv2.waitKey()
        frameCount+=1

    if ret == True:
        frame = imutils.resize(frame,width=400)
        frameCount+=1
        print(frameCount)
        cv2.imshow('Frame',frame)

        start = time.time()
        thresh,maskT=face_detect_and_thresh(frame) # rest of frames are sent to a function to have a threshold/overlap with mask
        cv2.imshow("img_rgb",thresh)
        end = time.time()
        print(end - start)
        start = time.time()
        if final_sig:
            final_sig.append(MeanRGB(thresh,frame,final_sig[-1],min_value,max_value)) # The frames are then sent to spartialAverage to find RGB mean values
            print(min_value)
            print(max_value)
        else:
            temp,min_value,max_value =spartialAverage(maskT,frame)
            final_sig.append(temp)
        end = time.time()
        print(end - start)

        #  Those rgb values are appened to final_sig which will be used for spo2 estimation
        if cv2.waitKey(25) & 0xFF == ord('q'): #end the loop if your press 'q' or video reaches end
            break
        # if frameCount==32:
        #     break

  # Break the loop
    else:
        break

# When everything done, release
# the video capture object
cap.release()

# Closes all the frames
cv2.destroyAllWindows()


pickle.dump(final_sig, open( "spo2.p", "wb" ) ) #For debugging you can try saving the signal as a pickle and run usingPick.py
print(final_sig)
result=SPooEsitmate(final_sig,length,length,seconds) # the final signal list is sent to SPooEsitmate function with length of the video
print(result)