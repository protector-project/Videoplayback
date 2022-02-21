docker build --pull --rm -f "Dockerfile" -t videoplayback:latest "."
docker run -it -p 5000:5000 videoplayback
# test url http://localhost:5000/objects/rec-piazza-2-sett-3-20211207T131213-20211207T131513-mjpeg/30
