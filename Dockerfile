FROM python:3.11-alpine

WORKDIR /app

COPY requirements.txt .
RUN pip3 install -r requirements.txt

RUN python3 -m spacy download en_core_web_lg
RUN python3 -m spacy download en_core_web_sm

COPY /mysite .

EXPOSE 8000

CMD ["python3", "manage.py", "runserver"]
