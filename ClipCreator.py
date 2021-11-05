from vidgear.gears import WriteGear
import cv2
import asyncio

@asyncio.coroutine
async def create_clip(video_name, timestamp, output_file):
    print("creating video")
    TIME_BEFORE_AFTER = 60
    video_file = video_name

    time_before = timestamp - TIME_BEFORE_AFTER
    if time_before < 0:
        time_before = 0
    time_after = timestamp + TIME_BEFORE_AFTER 
    cap = cv2.VideoCapture(video_file)
    frame_exists, img = cap.read()
    try:
        file_name = video_name + str(timestamp) + ".mp4"
        out = WriteGear(output_filename=file_name)

        while frame_exists:
            # get the current time of the frame
            frame_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000
            
            if (frame_time >= time_before) and (frame_time <= time_after):
                # write frame
                print(frame_time)
                out.write(img)

            if frame_time > time_after:
                break
            
            frame_exists, img = cap.read()

    except Exception as e:
        print(e)
        cap.release()
        out.close()
        return ""

    cap.release()
    out.close()

    output_file = file_name

    return file_name
