#!/usr/bin/env python
# import the necessary packages
import csv
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from imutils.video import VideoStream
from imutils.video import FPS
from rpi_lcd import LCD
from datetime import datetime
import face_recognition
import imutils
import pickle
import time
import cv2
import requests
lcd = LCD()


class FortiPi:
    # Emailing method, text param. is the reason why it was triggered
    # API Key and Token can be changed to your own
    # Updates the log file name: test.txt
    def send_Email(self, text):
        print("I am sending an email.")
        lcd.clear()
        lcd.text("Alerting Admin", 1)
        lcd.text("SENDING EMAIL....", 2)
        now = datetime.now()
        currtime = now.strftime("%H:%M:%S")
        with open("../rpiWebServer/static/test.txt", 'r+') as fp:
            lines = fp.readlines()     # lines is list of line, each element '...\n'
            # you can use any index if you know the line index
            lines.insert(0, f"{text} - {currtime}\n")
            # file pointer locates at the beginning to write the whole file again
            fp.seek(0)
            # write whole lists again to the same file
            fp.writelines(lines)
        return requests.post(
            "https://api.mailgun.net/v3/sandbox7fba7fd6c6c646da9e52f6be7ec525f7.mailgun.org/messages",
            files=[("attachment", ("image.jpg", open(
                "../rpiWebServer/static/image.jpg", "rb").read()))],
            auth=("api", "8135d582ba81860d1e072e1e826a407c-b36d2969-8feab554"),
            data={"from": 'hello@example.com',
                  "to": 'fortipi2secure@gmail.com',
                  "subject": "Visitor Alert",
                  "html": "<html>" + text + "</html>"})
    # Extracts data from csv file, and checks if keycard is inside the DB and returns True or False

    def verify_user(self):
        storagelist = []
        try:
            with open("DB.csv", "r") as file:
                csvr = csv.reader(file)
                next(csvr)
                for row in csvr:
                    storagelist.append(row)
        except:
            print("Error Opening File")
            return "File Error"
        finally:
            reader = SimpleMFRC522()
            try:
                print("Place Your Keycard to the Reader")
                lcd.clear()
                lcd.text("Place Keycard", 1)
                lcd.text("to the Reader", 2)
                id, text = reader.read()
                if [str(id), str(text).strip()] in storagelist:
                    print("Access Granted")
                    lcd.clear()
                    lcd.text("Access Granted", 1)
                    lcd.text(f"Welcome {text}", 2)
                    return "Verified"
                else:
                    print("Access Denied")
                    lcd.clear()
                    lcd.text("Access Denied", 1)
                    # might have a bug here, test with tyreses card
                    cv2.imwrite("../rpiWebServer/static/image.jpg",
                                self.find_Face.frame)
                    return False
            except:
                return "Unable to read fob"
            finally:
                GPIO.cleanup()
    # gets the known encodings from pickle file, Returns True if face encodings is known, else triggers email, SOURCE: https://github.com/carolinedunn/facial_recognition/blob/main/facial_req.py

    def find_Face(self):
        lcd.clear()
        lcd.text("Running FaceID", 1)
        lcd.text("Face The Camera", 2)
        # Initialize 'currentname' to trigger only when a new person is identified.
        currentname = "unknown"
        # Determine faces from encodings.pickle file model created from train_model.py
        encodingsP = "../rpiWebServer/encodings.pickle"

        # load the known faces and embeddings along with OpenCV's Haar
        # cascade for face detection
        print("[INFO] loading encodings + face detector...")
        data = pickle.loads(open(encodingsP, "rb").read(), encoding="latin1")

        # initialize the video stream and allow the camera sensor to warm up

        vs = VideoStream(usePiCamera=True).start()
        time.sleep(2.0)

        # start the FPS counter
        fps = FPS().start()

        while True:
            # grab the frame from the threaded video stream and resize it
            # to 500px (to speedup processing)
            frame = vs.read()
            frame = imutils.resize(frame, width=500)
            # Detect the fce boxes
            boxes = face_recognition.face_locations(frame)
            # compute the facial embeddings for each face bounding box
            encodings = face_recognition.face_encodings(frame, boxes)
            names = []

            # loop over the facial embeddings
            for encoding in encodings:
                # attempt to match each face in the input image to our known
                # encodings
                matches = face_recognition.compare_faces(
                    data["encodings"], encoding)
                name = "Unknown"  # if face is not recognized, then print Unknown

                # check to see if we have found a match
                if True in matches:
                    # find the indexes of all matched faces then initialize a
                    # dictionary to count the total number of times each face
                    # was matched
                    matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                    counts = {}

                    # loop over the matched indexes and maintain a count for
                    # each recognized face face
                    for i in matchedIdxs:
                        name = data["names"][i]
                        counts[name] = counts.get(name, 0) + 1

                    # determine the recognized face with the largest number
                    # of votes (note: in the event of an unlikely tie Python
                    # will select first entry in the dictionary)
                    name = max(counts, key=counts.get)

                    # If someone in your dataset is identified, print their name on the screen
                    if currentname != name:
                        currentname = name
                        print(currentname)
                        cv2.destroyAllWindows()
                        vs.stop()
                        return True
                else:
                    cv2.imwrite("../rpiWebServer/static/image.jpg", frame)
                    cv2.destroyAllWindows()
                    vs.stop()
                    return False

                # update the list of names
                names.append(name)

                if key == ord("q"):
                    break

            # loop over the recognized faces, places box on face. ONLY FOR DEVELOPMENT PURPOSE
            for ((top, right, bottom, left), name) in zip(boxes, names):
                # draw the predicted face name on the image - color is in BGR
                cv2.rectangle(frame, (left, top),
                              (right, bottom), (0, 255, 225), 2)
                y = top - 15 if top - 15 > 15 else top + 15
                cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                            .8, (0, 255, 255), 2)

            # display the image to our screen
            cv2.imshow("Facial Recognition is Running", frame)
            key = cv2.waitKey(1) & 0xFF

            # quit when 'q' key is pressed
            if key == ord("q"):
                break

            # update the FPS counter
            fps.update()

        # stop the timer and display FPS information
        fps.stop()
        print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
        print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

        # do a bit of cleanup
        cv2.destroyAllWindows()
        vs.stop()


def main():
    run = FortiPi()

    # Run the program in a loop
    while (1):
        # run find_face, and if returns True go to next auth step
        if run.find_Face():
            lcd.clear()
            lcd.text("Face Match", 'center')
            time.sleep(3)
            # run the rfid reader step, and if returns True open the lock
            if run.verify_user():
                GPIO.setmode(GPIO.BCM)
                GPIO.setwarnings(False)
                # gpio pin to change here
                GPIO.setup(23, GPIO.OUT)
                GPIO.output(23, GPIO.HIGH)
                # time of lock open can be changed here
                time.sleep(3)
                GPIO.output(23, GPIO.LOW)
                now = datetime.now()
                currtime = now.strftime("%H:%M:%S")
                # Update log file to state door has been open
                with open("../rpiWebServer/static/test.txt", 'r+') as fp:
                    lines = fp.readlines()     # lines is list of line, each element '...\n'
                    # you can use any index if you know the line index
                    lines.insert(0, f"Entry- {currtime}\n")
                    # file pointer locates at the beginning to write the whole file again
                    fp.seek(0)
                    # write whole lists again to the same file
                    fp.writelines(lines)
            else:
                # Send the email, with the step that has been failed
                run.send_Email("Invalid Keycard")
                time.sleep(2)

        else:
            # Send the email, with the step that has been failed
            run.send_Email("Stranger at Your Door")
            time.sleep(2)


if __name__ == '__main__':
    main()
