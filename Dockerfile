FROM python:3.10-slim-bullseye

COPY ./requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt

COPY ./ /app/src

WORKDIR /app/src

CMD ["python", "main.py"]
