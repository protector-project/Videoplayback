FROM nvcr.io/nvidia/pytorch:21.06-py3
COPY . /app/
WORKDIR /app
RUN apt update -y
RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get -y install tzdata
RUN apt install ffmpeg -y
RUN pip3 install vidgear Flask seaborn aioflask
ENTRYPOINT [ "python3" ]
CMD [ "app2.py" ]