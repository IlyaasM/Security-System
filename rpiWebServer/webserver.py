from flask import Flask, request, render_template
import Write
import Read
import os
import csv
import subprocess
import RPi.GPIO as GPIO
import time
from werkzeug.utils import secure_filename

app = Flask(__name__)

# login html page, first page when ip:port is typed in a browser


@app.route('/')
def my_form():

    return render_template('/Login.html')

# after you submit login form goes to index, also checks if the password and email are valid
# currently hardcoded login info, can be changed here
# future developement: create section on admin portal for this part


@app.route('/logged-in', methods=['POST'])
def logged_in():
    os.system("sh copy_image.sh")
    if request.method == 'POST':
        password = request.form['password']
        email = request.form['email']
        if password == "admin" and email == "admin@admin.com":
            os.system("sh copy_image.sh")

            return render_template('index.html')

# add name to rfid reader, then read the UID of key and add name and uid to DB.csv
# updating log file, page must be hard reloaded
# future development: figure out a way to bypass cached files, so it can be updated live


@app.route('/write-fob', methods=['POST'])
def RFID_Write():
    if request.method == 'POST':
        name = request.form['name']
        Write.write_key(name)  # no return
        key_id = Read.read_key()  # returns the keys uid
        with open('static/DB.csv', 'a', newline='') as csvfile:
            # Create a CSV writer object
            writer = csv.writer(csvfile)
            # Write the name and ID to the CSV file
            writer.writerow([key_id, name])
        with open('../facial_recognition/DB.csv', 'a') as csvfile:
            # Create a CSV writer object
            writer = csv.writer(csvfile)
            # Write the name and ID to the CSV file
            writer.writerow([key_id, name])

        with open("static/test.txt", 'r+') as fp:
            lines = fp.readlines()     # lines is list of line, each element '...\n'
            # you can use any index if you know the line index
            lines.insert(0, f"{name}'s keycard added to the Database\n")
            # file pointer locates at the beginning to write the whole file again
            fp.seek(0)
            # write whole lists again to the same file
            fp.writelines(lines)

        return render_template('index.html')

# creates the directory with the name user typed, run the training program to add face to encodings file
# update the log file with what has been done
# no error checking to see if its an image, this is already done in html code, to prevent attackers from running scripts


@app.route('/uploadimgs', methods=['POST'])
def upload():
    name = request.form['name']
    directory_name = f"../facial_recognition/dataset/{name}"
    # create a directory for uploaded files if it doesn't exist
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)

    # get the uploaded files from the request
    files = request.files.getlist('imgs')

    # save each file to the uploads directory
    for idx, file in enumerate(files):
        file.save(os.path.join(directory_name, f"image_{idx}.jpg"))
    # subprocess.run(["python3", "/home/pi/facial_recognition/train_model.py"])
    os.system("python3 train_model.py")
    with open("static/test.txt", 'r+') as fp:
        lines = fp.readlines()     # lines is list of line, each element '...\n'
        # you can use any index if you know the line index
        lines.insert(0, f"{name}'s face encodings added to the Dataset\n")
        # file pointer locates at the beginning to write the whole file again
        fp.seek(0)
        fp.writelines(lines)       # write whole lists again to the same file

    return render_template('index.html')

# opens the door, gpio pin can be changed here
# comment out lines with "#1 and #2" to make it open forever
# to close lock in future, uncomment next code block, log file is updated after procedures
# THIS IS NOT ADVISED!!


@app.route('/unlock', methods=['POST'])
def open_door():

    GPIO.setwarnings(False)
    GPIO.setup(23, GPIO.OUT)
    GPIO.output(23, GPIO.HIGH)
    print("door is opened")

    time.sleep(3)  # 1
    GPIO.output(23, GPIO.LOW)  # 2
    with open("static/test.txt", 'r+') as fp:
        lines = fp.readlines()     # lines is list of line, each element '...\n'
        # you can use any index if you know the line index
        lines.insert(0, "DOOR UNLOCKED FROM CONTROL PANEL\n")
        # file pointer locates at the beginning to write the whole file again
        fp.seek(0)
        fp.writelines(lines)       # write whole lists again to the same file

    return render_template('index.html')


'''
@app.route('/lock', methods=['POST'])
def close_door():

    GPIO.setwarnings(False)
    GPIO.setup(23, GPIO.OUT)
    GPIO.output(23, GPIO.LOW)
    with open("static/test.txt", 'r+') as fp:
        lines = fp.readlines()     # lines is list of line, each element '...\n'
        # you can use any index if you know the line index
        lines.insert(0, "DOOR LOCKED FROM CONTROL PANEL\n")
        # file pointer locates at the beginning to write the whole file again
        fp.seek(0)
        fp.writelines(lines)       # write whole lists again to the same file

    return render_template('index.html')
'''


if __name__ == '__main__':
    app.run(debug=True, port=5000, host='192.168.2.141')
