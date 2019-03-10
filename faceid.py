from blockchain import get_balance, private_key_to_address, pin_code_to_private_key, normalize_value

import json
import requests
import cognitive_face as cf
import cv2
import os

from sys import argv


def read_args():
    args = dict()

    if "--find" in argv:
        find_index = argv.index("--find")
        args["find"] = argv[find_index + 1]

    elif "--balance" in argv:
        balance_index = argv.index("--balance")
        args["balance"] = argv[balance_index + 1]
    elif "--send" in argv:
        send_index = argv.index("--send")
        args['send'] = argv[send_index+1]
        args['pin'] = argv[send_index + 2]
        args['phone'] = argv[send_index + 3]
        args['value'] = argv[send_index + 4]
    return args


def init():
    with open("faceapi.json", "r", encoding="utf-8") as file:
        loaded_file = json.load(file)
        subscription_key = loaded_file["key"]
        base_url = loaded_file["serviceUrl"]
        personGroupId = loaded_file["groupId"]

    cf.Key.set(subscription_key)
    cf.BaseUrl.set(base_url)

    return subscription_key, base_url, personGroupId


def frames_capture(filename, frames_number):
    cap = cv2.VideoCapture(filename)
    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if length < frames_number:
        return
    else:
        distance = round(length / (frames_number - 1))
        specific_frames = [distance * i for i in range(frames_number - 1)]
        specific_frames.append(length - 1)

        frames = list()

        while cap.isOpened():
            for count in range(length):
                ret, frame = cap.read()

                if count in specific_frames:
                    face = cv2.imencode(".jpg", frame)[1].tobytes()
                    frames.append(face)

            break

    cap.release()

    return frames


def identify(args, personGroupId, subscription_key):
    frames = frames_capture(args["find"], 5)

    if not frames:
        if os.path.exists("person.json"):
            os.remove("perWIP: Develop
son.json")
        return 'The video does not follow requirements'

    person_faces = list()

    params_checking = {"returnFaceId": "true", "returnFaceLandmarks": "false", "returnFaceAttributes": ""}
    headers_checking = {"Content-Type": "application/octet-stream", "Ocp-Apim-Subscription-Key": subscription_key}

    for frame in frames:
        face = requests.post("https://westeurope.api.cognitive.microsoft.com/face/v1.0/detect",
                             params=json.dumps(params_checking),
                             headers=headers_checking, data=frame).json()

        if len(face) == 0:
            if os.path.exists("person.json"):
                os.remove("person.json")
            return "The video does not follow requirements"
        else:
            person_faces.append(face[0]["faceId"])

    response_group_list = requests.get("https://westeurope.api.cognitive.microsoft.com/face/v1.0/persongroups/",
                                       headers={"Ocp-Apim-Subscription-Key": subscription_key}).json()
    group_list = list()

    for group in range(len(response_group_list)):
        group_list.append(response_group_list[group]["personGroupId"])

    if personGroupId not in group_list:
        if os.path.exists("person.json"):
            os.remove("person.json")
        return "The service is not ready"

    elif (requests.get(f"https://westeurope.api.cognitive.microsoft.com/face/v1.0/"
                          f"persongroups/{personGroupId}", params={"personGroupId": personGroupId},
                          headers={"Ocp-Apim-Subscription-Key": subscription_key}).json()["userData"]) == "untrained":
        if os.path.exists("person.json"):
            os.remove("person.json")
        return "The service is not ready"

    else:
        identify_response = requests.post("https://westeurope.api.cognitive.microsoft.com/face/v1.0/identify",
                                          headers={"Content-Type": "application/json",
                                                   "Ocp-Apim-Subscription-Key": subscription_key},
                                          data=json.dumps({"faceIds": person_faces, "personGroupId": personGroupId,
                                                           "maxNumOfCandidatesReturned": 1,
                                                           "confidenceThreshold": 0.5})).json()
        counter = 0

        for i in range(5):
            if not len(identify_response[i]["candidates"]):
                counter += 1

        if counter > 0:
            if os.path.exists("person.json"):
                os.remove("person.json")
            return "The person was not found"
        else:
            id = identify_response[0]["candidates"][0]["personId"]

            for ids in identify_response:
                if id != ids["candidates"][0]["personId"]:
                    if os.path.exists("person.json"):
                        os.remove("person.json")
                    return "The person was not found"

            with open("person.json", "w", encoding="utf-8") as file:
                json.dump({"id": id}, file, indent=4)
            return f"{id} identified"


args = read_args()

if "balance" in args:
    private_key = args["balance"]
    address = private_key_to_address(private_key)
#
    print('Your balance is %s' % normalize_value(get_balance(address)))

if "find" in args:
    key, url, groupId = init()
    print(identify(args, groupId, key))







