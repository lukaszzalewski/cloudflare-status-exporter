FROM python:3.9-alpine

COPY requirements.txt ./
COPY app.py ./
RUN ls
RUN pip install -r ./requirements.txt

ENV FLASK_APP=app.py
ENV FLASK_ENV=production

CMD ["flask", "run"]