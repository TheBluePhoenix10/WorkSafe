Even though it works with any camera device and you can feed it json data from any embedded device using wifi, this repository was developed to complement the WorkSafe device. This readme contains all basic information to run this software.

### **Dependencies:**
Python 3.6.12 (The software won't work on python versions other than 3.6)
OpenCV 4.5.1 and OpenCV contrib
imutils 0.5.3
Numpy 1.19.5
dlib 19.8.1 (install cmake first to install dlib)
PyQT 4 or 5 both are supported
scipy
pandas
xlsxwriter
requests
pythonping
face_recognition
bcrypt
pymongo
getmac
pyperclip

Once all dependancies are installed, you will be able to run the 2 main code files- WorkSafe.py and batchPhoto.py

### **main scripts:**
**batchPhoto.py** is used to collect photos for the face recognition functionality of the main software and can also retrain the model with the newly added faces. You can select how many photos you want to add alongwith the name of the person being added.

**WorkSafe.py** is the main script that can run our GUI and software. As this software is developed to be commercially deployable, it contains a triple verification system. You will require a license key (you can ask for a test license by contacting me on this mail id: dishantshah1998@gmail.com) and will have to register on our website (there is a registration button inside the setup which will redirect you to our website for registration). The registration page on our website will ask for your email id, mac id and activation key simultaneously. Once registered successfully, you will have to enter all these details again once, after which you will be able to run the software without having to enter the license key again and again for a period of 30 days (changing the date on your Desktop device will not reset this period). 

Once activated, you will be able to save and use any number of ip cameras, web cameras or worksafe devices. Once a device is set up and saved, you can directly select the run option to open the GUI and select a saved device. For the system to work, everything has to be on the same local wifi network.

### **Further instructions**
All the steps and details on how to use the various buttons and functions of our main GUI software as well the batchPhoto script are documented in a instruction manual that we have created. It can be viewed here: https://drive.google.com/file/d/1HKTsD9kUfiyijpllLyKm9hIiLULIxXuX/view?usp=sharing

### **Folder Descriptions:**
The **dataset** folder contains the saved images taken using the batchPhoto.py script. You can directly save photos of a person you would like to add to the FR database inside a folder with the same name as that of the person. 
If fever is detected, you will be sent an e-mail with the photo and vital stats of the person screened. The photo will be saved in the "**email_content**" folder
**excel_sheets** folder contains two excel files, one containing the data of the people in the FR database (details.xlsx) and the other which is an automated attendance report (attendance.xlsx). The name of the personnel/employee entered in the details.xlsx should be same as their respective folder's name containing the images of the respective personnel/employee. The attendance.xlsx creates a separate sheet for each day and saves the vital stats data against the identified personnel's name with the time stamp. If face not recognized, the name will show up to be unknown.
**models:** contains models used for FR
**password:** contains the mac-id, email-id and activation-key used to register and unlock the software
**recordings:** contains video recordings that can be saved using the Recoding button of the main GUI software. 
**resources:** A few images of the background and button icons used by the software
**saved_devices:** contains the saved camera and worksafe device configurations
**skin_detector:** A folder containing scripts pertaining to skin detection

For other details, contact me on my e-mail id or use the instruction manual, both of which are provided above.

I will be adding additional functionalities like fall detection, hazard sign detection, PPE gear detection, etc. in the future. 


