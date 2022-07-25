FROM python:3.9-slim-buster

WORKDIR /app

COPY ./requirements.txt ./
RUN pip install -r requirements.txt

COPY ./index.py ./

CMD ["python", "index.py"]