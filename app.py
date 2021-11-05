#!/usr/bin/env python
from os import listdir
from os.path import isfile, join
import asyncio
import threading

import cv2
from flask import Flask, Response, render_template
from vidgear.gears import VideoGear
from ClipCreator import create_clip

VIDEO_FOLDER = "static/"

filenames = [f for f in listdir(VIDEO_FOLDER) if isfile(join(VIDEO_FOLDER, f))]
filenames_without_extension = [name.split(".avi")[0] for name in filenames]
print(filenames_without_extension)

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


def gen(videoname):
    stream = VideoGear(source=videoname).start()
    while True:
        frame = stream.read()
        if frame is None:
            break
        ret, buffer = cv2.imencode(".jpg", frame)
        frame = buffer.tobytes()
        yield (
            b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
        )  # concat frame one by one and show result


@app.route("/stream/<id>")
def video_feed(id):
    video_name = str(id)
    if video_name not in filenames_without_extension:
        return Response("Not Found")
    video_name = VIDEO_FOLDER + video_name + ".mp4"
    return Response(
        gen(video_name), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/video/<id>/<timestamp>")
def video_feed2(id, timestamp):
    video_name = str(id)
    timestamp = str(timestamp)
    if video_name not in filenames_without_extension:
        return Response("Not Found")
    video_name = video_name + ".mp4"
    return render_template("video_player.html", video_name=video_name, timestamp=5)

@app.route("/objects/<id>/<timestamp>")
async def process_video(id, timestamp):
    video_name = str(id)
    timestamp = int(timestamp)
    if video_name not in filenames_without_extension:
        return Response("Not Found")
    FILE_FOLDER = "static/"
    video_name = FILE_FOLDER + video_name + ".avi"
    output_file = ""
    output_file = video_name + str(timestamp) + ".mp4"
    output_file = output_file.replace("static/", "")
    future = asyncio.ensure_future(create_clip(video_name, timestamp, output_file))
    print('Waiting for a few seconds')
    
    return render_template("video_player.html", video_name=output_file, timestamp=30)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, threaded=True)
