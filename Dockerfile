FROM python:3.8.1-alpine3.11
RUN mkdir -p /controller
RUN pip install --upgrade pip && apk --no-cache add musl-dev g++
ADD requirements.txt /
RUN pip install -r /requirements.txt && rm -rf /requirements.txt
ADD controller.py /controller/
ADD config/ /controller/config
ADD gooseka_control/ /controller/gooseka_control
WORKDIR /controller
CMD ["python3","controller.py","--config_file","config/defaults.yaml"]