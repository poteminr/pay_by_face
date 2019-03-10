#!/usr/bin/env python

### Put your code below this comment ###
import json
import requests
import cognitive_face as cf
import cv2

from sys import argv


class FaceEngine:
    def __init__(self):
        with open("faceapi.json", "r", encoding="utf-8") as file:
            settings = json.load(file)
        self.subscription_key = settings["key"]
        self.url = settings["serviceUrl"]
        self.personGroupId = settings["groupId"]

        cf.Key.set(self.subscription_key)
        cf.BaseUrl.set(self.url)

    @staticmethod
    def frames_capture(filename, frames_number):
        cap = cv2.VideoCapture(filename)
        length_in_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        if length_in_frames < frames_number:
            return
        else:
            distance = round(length_in_frames / (frames_number - 1))
            specific_frames = [distance * i for i in range(frames_number - 1)]
            specific_frames.append(length_in_frames - 1)

            frames = list()

            while cap.isOpened():
                for count in range(length_in_frames):
                    frame = cap.read()[1]

                    if count in specific_frames:
                        face = cv2.imencode(".jpg", frame)[1].tobytes()
                        frames.append(face)

                break

        cap.release()

        return frames

    def create_group(self):
        requests.put(f"{self.url}persongroups/{self.personGroupId}",
                     params={"personGroupId": self.personGroupId},
                     headers={"Content-Type": "application/json", "Ocp-Apim-Subscription-Key": self.subscription_key},
                     data=json.dumps({"name": self.personGroupId, "userData": "untrained."}))

    def set_group_status(self, status):
        requests.patch(f"{self.url}persongroups/{self.personGroupId}", params={"personGroupId": self.personGroupId},
                       headers={"Content-Type": "application/json",
                                "Ocp-Apim-Subscription-Key": self.subscription_key},
                       data=json.dumps({"name": self.personGroupId,
                                        "userData": status}))

    def contain_face(self, frames):
        for frame in frames:
            face = requests.post(f"{self.url}detect",
                                 params=json.dumps({"returnFaceId": "false",
                                                    "returnFaceLandmarks": "false", "returnFaceAttributes": ""}),
                                 headers={"Content-Type": "application/octet-stream",
                                          "Ocp-Apim-Subscription-Key": self.subscription_key}, data=frame).json()

            if len(face) == 0:
                return False

        return True

    def create_person(self):
        return requests.post(f"{self.url}persongroups/{self.personGroupId}/persons",
                             params=json.dumps({"personGroupId": self.personGroupId}),
                             headers={"Content-Type": "application/json",
                                      "Ocp-Apim-Subscription-Key": self.subscription_key},
                             data=json.dumps({"name": "Username",
                                              "userData": "User-provided data attached to the person."})).json()[
            "personId"]

    def get_persons(self):
        response = requests.get(f"{self.url}persongroups/{self.personGroupId}/persons",
                                headers={"Ocp-Apim-Subscription-Key": self.subscription_key}).json()

        if "error" in response and response["error"]["code"] == "PersonGroupNotFound":
            return "The group does not exist"
        elif len(response) == 0:
            return "No persons found"

        return [person["personId"] for person in response]

    def get_groups(self):
        return [group["personGroupId"] for group in requests.get(f"{self.url}persongroups/",
                                                                 headers={
                                                                     "Ocp-Apim-Subscription-Key": self.subscription_key}).json()]

    def simple_add_faces(self, frames):
        if not frames or not self.contain_face(frames):
            print("Video does not contain any face")
            return None, None

        if self.personGroupId not in self.get_groups():
            self.create_group()

        personId = self.create_person()

        faces = [requests.post(f"{self.url}persongroups/{self.personGroupId}/persons/{personId}/persistedFaces",
                               params=json.dumps({"personGroupId": self.personGroupId,
                                                  "personId": personId}),
                               headers={"Content-Type": "application/octet-stream",
                                        "Ocp-Apim-Subscription-Key": self.subscription_key},
                               data=frame).json()['persistedFaceId'] for frame in frames]

        self.set_group_status("untrained")

        return personId, faces

    def simple_add(self, args):
        frames = self.frames_capture(args['simple-add'], 5)

        personId, faces = self.simple_add_faces(frames)

        if personId:
            print("5 frames extracted")
            print(f"PersonId: {personId}")
            print("FaceIds")
            print("=======")

            for n, faceId in enumerate(faces):
                print(faceId, end='')

                if n != len(faces) - 1:
                    print()

    def delete_person(self, args):
        if self.personGroupId not in self.get_groups():
            return "The group does not exist"

        persons = self.get_persons()

        if persons == "No persons found" or persons == "The group does not exist" or args["del"] not in persons:
            return "The person does not exist"

        elif args["del"] in persons:
            requests.delete(f"{self.url}persongroups/{self.personGroupId}/persons/{args['del']}",
                            headers={"Ocp-Apim-Subscription-Key": self.subscription_key},
                            params={"personGroupId": self.personGroupId, "personId": args["del"]})

            self.set_group_status("untrained")

            return "Person deleted"

    def get_group_status(self):
        return requests.get(f"{self.url}persongroups/{self.personGroupId}",
                            params={"personGroupId": self.personGroupId},
                            headers={"Ocp-Apim-Subscription-Key": self.subscription_key}).json()["userData"]

    def train(self):
        if self.personGroupId not in self.get_groups() or self.get_persons() == "No persons found":
            return "There is nothing to train"

        status = self.get_group_status()

        if status == "untrained":
            requests.post(f"{self.url}persongroups/{self.personGroupId}/train",
                          params={"personGroupId": self.personGroupId},
                          headers={"Ocp-Apim-Subscription-Key": self.subscription_key})

            self.set_group_status("trained")

            return "Training successfully started"

        elif status == "trained":
            return "Already trained"

    def handle_args(self, args):
        if "simple-add" in args:
            self.simple_add(args)

        elif "list" in args:
            persons_list = self.get_persons()
            if persons_list == "No persons found" or persons_list == "The group does not exist":
                print(persons_list)

            else:
                print("Persons IDs:")
                for person in persons_list:
                    print(person)

        elif "del" in args:
            print(self.delete_person(args))

        elif "train" in args:
            print(self.train())

        # elif "filenames" in args:
        #     add()


def read_args():
    args = dict()

    if "--simple-add" in argv:
        simple_add_index = argv.index("--simple-add")
        args["simple-add"] = argv[simple_add_index + 1]

    if "--list" in argv:
        args["list"] = True

    if "--del" in argv:
        del_index = argv.index("--del")
        args["del"] = argv[del_index + 1]

    if "--train" in argv:
        args["train"] = True

    if "--find" in argv:
        find_index = argv.index("--find")
        args["find"] = argv[find_index + 1]

    # if "--add" in argv:
        # add_index = argv.index("--add")
        # args["filenames"] = argv[2:]
    #     # args["filename_1"] = argv[add_index + 1]  # ? indexes "[", list of filenames
    #     # args["filename_2"] = argv[add_index + 2]
    #     # args["filename_3"] = argv[add_index + 3]
    #     # args["filename_4"] = argv[add_index + 4]
    #     # args["filename_5"] = argv[add_index + 5]

    return args


# def add():
#     def video_checking(args, url, subscription_key):
#         videos_frames = list()
#         for video in args["filenames"]:
#             videos_frames.append(frames_capture(video, 5))
#
#         if args["filenames"][0]:
#             frames = frames_capture(args["filenames"][0], 5)
#
#             for frame in frames:
#                 res = requests.post(f"{url}detect",
#                                  params={"returnFaceId": "false",
#                                                     "returnFaceLandmarks": "false", "returnFaceAttributes": "headPose"},
#                                  headers={"Content-Type": "application/octet-stream",
#                                           "Ocp-Apim-Subscription-Key": subscription_key}, data=frame).json()
#
#                 if abs(res[0]["faceAttributes"]["headPose"]["pitch"]) > 5 or \
#                         abs(res[0]["faceAttributes"]["headPose"]["roll"]) > 5 or \
#                         abs(res[0]["faceAttributes"]["headPose"]["yaw"]) > 5: # need add eye/mouth closed checking
#                     return "Base video does not follow requirements"
#
#             personId, faces = simple_add_faces(frames, groupId, key, url)
#
#             if personId:
#                 print("5 frames extracted")
#                 print(f"PersonId: {personId}")
#                 print("FaceIds")
#                 print("=======")
#
#                 for n, faceId in enumerate(faces):
#                     print(faceId, end='')
#
#                     if n != len(faces) - 1:
#                         print()
#
#         if videos_frames[1]:
#             for frame in videos_frames[1]:
#
#
#     print(video_checking(args, url, key))
#
#     # def add_faces(args):
#     #     if not frames or not contain_face(frames, subscription_key, url):
#     #         print("Video does not contain any face")
#     #         return None, None

face_engine = FaceEngine()
args = read_args()
face_engine.handle_args(args)


