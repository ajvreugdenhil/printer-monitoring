FROM python:3.8.6
COPY requirements.txt /src/requirements.txt
RUN pip3 install -r /src/requirements.txt
COPY app /src/app
WORKDIR /src/app
EXPOSE 8000
ENTRYPOINT ["python3","main.py"]
