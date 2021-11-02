#!/usr/bin/env python
from os import listdir
from os.path import isfile, join

import cv2
from flask import Flask, Response, render_template
from vidgear.gears import VideoGear

VIDEO_FOLDER = "static/"

filenames = [f for f in listdir(VIDEO_FOLDER) if isfile(join(VIDEO_FOLDER, f))]
filenames_without_extension = [name.split(".mp4")[0] for name in filenames]
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, threaded=True)
