FROM python:latest

RUN apt-get update -y
RUN apt-get upgrade -y

WORKDIR /clubfeast

RUN mkdir data

COPY requirements.txt /clubfeast/
COPY code.py /clubfeast/

RUN pip install -r requirements.txt

CMD ["python", "code.py"]