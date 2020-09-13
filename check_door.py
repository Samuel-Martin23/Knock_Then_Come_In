import serial
import platform
from time import sleep
from getpass import getuser
from datetime import datetime
from serial.tools import list_ports
from check_webcam import (take_picture, check_person_with_trained_data)


def main() -> None:
    operating_system: str = platform.system()
    user_name: str = getuser()
    serial_port: str = [str(port).split(" ")[0] for port in list_ports.comports() if "Bluetooth" not in str(port)][0]

    if operating_system == "Windows":
        home_folder_path: str = f"C:\\Users\\{user_name}"
    else:
        home_folder_path: str = f"/Users/{user_name}"

    serial_com: serial.serialposix.Serial = serial.Serial(serial_port, 9600)
    serial_com.timeout = 1

    while True:
        try:
            distance: int = int(serial_com.readline().decode("ascii").strip())
        except ValueError:
            distance = 150

        print(distance)

        # These values are subject to change.
        if 130 <= distance <= 140:
            with open(home_folder_path + "/door_tracker.txt", 'a') as file:
                date: str = datetime.now().strftime("%B %d, %Y at %H:%M")
                file.write("Door opened on {}\n".format(date))

            take_picture(home_folder_path + "/Camera_Images")
            # check_person_with_images(home_folder_path + "/Camera_Images", operating_system, user_name)
            check_person_with_trained_data(home_folder_path + "/Camera_Images")
            serial_com.close()
            sleep(1)
            serial_com: serial.serialposix.Serial = serial.Serial(serial_port, 9600)
            serial_com.timeout = 1


sleep(5)
main()
