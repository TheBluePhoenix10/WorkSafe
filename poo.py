import os
for file in os.listdir("saved_devices/"):
    if file.endswith(".pickle"):
        print(os.path.join("saved_devices/", file))