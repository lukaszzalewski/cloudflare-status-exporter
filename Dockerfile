FROM python:3.9-alpine

RUN mkdir app
WORKDIR /app
COPY requirements.txt app.py ./
RUN pip install -r ./requirements.txt

ENV FLASK_APP=app.py
ENV FLASK_ENV=production

EXPOSE 8000
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]