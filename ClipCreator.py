from vidgear.gears import WriteGear
import cv2
import asyncio
from ObjectDetector import ObjectDetector

o = ObjectDetector()
cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

@asyncio.coroutine
async def create_clip(video_name, timestamp, type):
    if type not in ['all', 'raw', 'obj', 'anon']:
        type = 'raw'
    TIME_BEFORE_AFTER = 10
    video_file = video_name

    time_before = timestamp - TIME_BEFORE_AFTER
    if time_before < 0:
        time_before = 0
    time_after = timestamp + TIME_BEFORE_AFTER 
    cap = cv2.VideoCapture(video_file)
    frame_exists, img = cap.read()
    try:
        if (type == 'raw') or (type == 'all'):
            file_name = video_name + str(timestamp) + ".mp4"
            out = WriteGear(output_filename=file_name)
        if (type == 'obj') or (type == 'all'):
            boxes_file_name = video_name + str(timestamp) + "_objects" +".mp4"
            out_boxes = WriteGear(output_filename=boxes_file_name)
        if (type == 'anon') or (type == 'all'):
            anon_file_name = video_name + str(timestamp) + "_anon" +".mp4"
            out_anon = WriteGear(output_filename=anon_file_name)

        while frame_exists:
            # get the current time of the frame
            frame_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000
            
            if (frame_time >= time_before) and (frame_time <= time_after):
                print(frame_time)
                # write frame
                if (type == 'raw') or (type == 'all'):
                    out.write(img)

                # process anonymize
                if (type == 'anon') or (type == 'all'):
                    bw = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    #blur = find_and_blur(bw, img)
                    out_anon.write(bw)

                # process object detector
                if (type == 'obj') or (type == 'all'):
                    results = o.score_frame(img)
                    frame = o.plot_boxes(results, img)
                    out_boxes.write(frame)


            if frame_time > time_after:
                break
            
            frame_exists, img = cap.read()

    except Exception as e:
        print(e)
        cap.release()
        if (type == 'raw') or (type == 'all'):
            out.close()
        if (type == 'obj') or (type == 'all'):
            out_boxes.close()
        if (type == 'anon') or (type == 'all'):
            out_anon.close()
        return ""

    cap.release()

    if (type == 'raw') or (type == 'all'):
        out.close()
    if (type == 'obj') or (type == 'all'):
        out_boxes.close()
    if (type == 'anon') or (type == 'all'):
        out_anon.close()

    return file_name


def find_and_blur(bw, color): 
    # detect al faces
    faces = cascade.detectMultiScale(bw, 1.1, 4)
    # get the locations of the faces
    for (x, y, w, h) in faces:
        # select the areas where the face was found
        roi_color = color[y:y+h, x:x+w]
        # blur the colored image
        blur = cv2.GaussianBlur(roi_color, (101,101), 0)
        # Insert ROI back into image
        color[y:y+h, x:x+w] = blur            
    
    # return the blurred image
    return color
