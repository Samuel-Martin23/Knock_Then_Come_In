import cv2
import numpy
import face_recognition as fr
from time import sleep
from shutil import rmtree
from requests import post
from os import (listdir, mkdir)
from subprocess import (Popen, PIPE)
from check_encodings import get_list_of_encodings
from typing import (Dict, Tuple, BinaryIO, List, Union)


def take_picture(camera_pics_dir_path: str) -> None:
    camera_port: int = 0
    i: int
    camera: cv2.VideoCapture = cv2.VideoCapture(camera_port)

    mkdir(camera_pics_dir_path)
    # This value is subject to change.
    sleep(0.5)
    for i in range(0, 5):
        image: numpy.ndarray = camera.read()[1]
        cv2.imwrite(camera_pics_dir_path + f"/webcam_pic_{i}.png", image)
        sleep(0.05)


def check_person_with_images(camera_pics_dir_path: str, operating_system: str, user_name: str) -> None:
    image_name: str
    known_face_encodings: List[numpy.ndarray] = []
    matches: List[numpy.bool_]
    image_path: str

    if operating_system == "Windows":
        known_faces_dir: str = sys_output(operating_system, f"cd /Users/{user_name} && dir /AD /s /b KNOWN_FACES")
    else:
        known_faces_dir: str = sys_output(operating_system, "find", "/Users", "-name", "KNOWN_FACES")

    for image_name in listdir(known_faces_dir):
        if image_name != ".DS_Store":
            image: numpy.ndarray = fr.load_image_file(f"{known_faces_dir}/{image_name}")
            encoding: numpy.ndarray = fr.face_encodings(image)[0]
            known_face_encodings.append(encoding)

    matches, image_path = get_lowest_tolerance(camera_pics_dir_path, known_face_encodings)

    if not matches:
        print("Can not detect face.")
        rmtree(camera_pics_dir_path)
        return

    if False in matches:
        print("Someone is here...")
        send_notification("Door Opened", "Who was it?", image_path)

    rmtree(camera_pics_dir_path)


def check_person_with_trained_data(camera_pics_dir_path: str) -> None:
    matches: List[numpy.bool_]
    image_path: str
    matches, image_path = get_lowest_tolerance(camera_pics_dir_path)

    if not matches:
        print("Can not detect face.")
        rmtree(camera_pics_dir_path)
        return

    if False in matches:
        print("Someone is here...")
        send_notification("Door Opened", "Who was it?", image_path)

    rmtree(camera_pics_dir_path)


def get_lowest_tolerance(camera_pics_dir_path: str, encodings: List[numpy.ndarray] = None) -> \
        Tuple[List[numpy.bool_], str]:

    if encodings is None:
        encodings = get_list_of_encodings()

    i: int
    webcam_image_path: str = camera_pics_dir_path + "/webcam_pic_{}.png"
    face_encoding: numpy.ndarray
    current_tolerance: float
    lowest_tolerance: float = 0.70

    # This value is subject to change.
    tolerance: float = 0.50

    matches: List[numpy.bool_] = []
    track_index: int = 0

    for i in range(0, 5):
        face_cam_image: numpy.ndarray = fr.load_image_file(webcam_image_path.format(i))
        face_locations: List[Tuple] = fr.face_locations(face_cam_image)

        if not face_locations:
            continue

        face_encodings: List[numpy.ndarray] = fr.face_encodings(face_cam_image, face_locations, model="large")

        for face_encoding in face_encodings:
            current_tolerances: Union[numpy.ndarray, float] = fr.face_distance(encodings, face_encoding)
            for current_tolerance in current_tolerances:
                if current_tolerance < lowest_tolerance:
                    lowest_tolerance = current_tolerance
                    matches = list(current_tolerances <= tolerance)
                    track_index = i

    return matches, webcam_image_path.format(track_index)


def send_notification(title_text_message: str, body_text_message: str, image_path: str = "") -> None:
    user_token: str = ""
    user_key: str = ""
    image_file: Dict[str, Tuple[str, BinaryIO, str]] = {}

    if image_path:
        image_file = {"attachment": ("image.jpg", open(image_path, "rb"), "image/jpeg")}

    post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": user_token,
            "user": user_key,
            "html": 1,
            "title": title_text_message,
            "message": body_text_message
        },
        files=image_file
    )

    sleep(2)


def sys_output(os: str, *cmd: str) -> Union[str, List[str]]:
    if os == "Windows":
        p: Popen = Popen(cmd[0], shell=True, stdout=PIPE)
    else:
        p: Popen = Popen(cmd, stdout=PIPE)
    output: List[str] = p.communicate()[0].decode("ascii").strip().split("\n")
    if len(output) == 1:
        return output[0]
    else:
        return output