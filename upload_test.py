import requests


with open("excel_sheets/attendance.xlsx", "rb") as a_file:

    file_dict = {"attendance": a_file}

    response = requests.post("http://localhost:3000/checkFile", files=file_dict)


    print(response)