from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtCore import QTimer, QPoint, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QLabel,QSplashScreen 
from PyQt5.QtWidgets import QWidget, QAction, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QFont, QPainter, QImage, QTextCursor,QPixmap
from PyQt5 import QtCore, QtGui
import sys 
import cv2
import os 

global name
name = ''
    
class SetupWindow(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        layout = QGridLayout()
        self.setLayout(layout)

        button = QPushButton("Proceed", self) 
  
        # setting geometry of button 
        button.setGeometry(200, 150, 100, 30) 
        layout.addWidget(button, 1, 0)
        # adding action to a button 
        button.clicked.connect(self.getText) 
        
    def getText(self):
        global name
        count = 0
        name, okPressed = QInputDialog.getText(self, "Password","Enter Password:", QLineEdit.Normal, "")
        self.close()
  
if __name__ == '__main__':
    state = QApplication(sys.argv)
    screen = SetupWindow()
    screen.show()
    state.exec()
    print(name)
    captureFlag=False
    FrameCount=30
    StoragePath = os.path.join('dataset/'+name+'/')
    isExist = os.path.exists(StoragePath)  
    if isExist:
        pass
    else:
        os.mkdir(StoragePath) 

        
    cap = cv2.VideoCapture(0)
    while(True):
        # Capture frame-by-frame
        ret, frame = cap.read()
        key = cv2.waitKey(1)
        if key == ord('p'):
            captureFlag=True
            FrameCount=30
        if captureFlag==True:
            cv2.imwrite(StoragePath+str(30-FrameCount)+'.png',frame)
            FrameCount= FrameCount-1
            if FrameCount<1:
                break 
        
        # Our operations on the frame come here
        # Display the resulting frame
        cv2.imshow('frame',frame)
        
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()