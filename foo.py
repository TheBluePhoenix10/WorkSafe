# importing libraries 
from PyQt5.QtWidgets import * 
from PyQt5 import QtCore, QtGui 
from PyQt5.QtGui import * 
from PyQt5.QtCore import * 
import sys 
import os

  
class Window(QMainWindow): 
  
    def __init__(self): 
        super().__init__() 
  
        # setting title 
        self.setWindowTitle("Python ") 
  
        # setting geometry 
        self.setGeometry(100, 100, 350, 450) 
  
        # calling method 
        self.UiComponents() 

        
        

        # showing all the widgets 
        self.show() 
  
    # method for widgets 
    def UiComponents(self): 
  
        self.l1 =QLabel('Please select your camera from the list below', self)
        self.l1.move(50,100)
        self.l1.adjustSize()
        self.l1.setAlignment(QtCore.Qt.AlignCenter) 
        # creating a combo box widget 
        self.combo_box = QComboBox(self) 
  
        for file in os.listdir("userPickles/"):
            if file.endswith(".pickle"):
                self.combo_box.addItem(file.split('.')[0])
        
        
        self.combo_box.move(115,200)
        
        
        self.button = QPushButton('Select Cam', self)

        
        self.button.clicked.connect(self.pushed)

        self.button.move(115,300)
        
        # adding items to combo box 
         
        

        

    
    def pushed(self):
        print(str(self.combo_box.currentText()))
        
        
# create pyqt5 app 
App = QApplication(sys.argv) 
  
# create the instance of our Window 
window = Window() 
  
# start the app 
sys.exit(App.exec()) 