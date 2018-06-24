FROM python:3.6-slim-stretch
ENV PYTHONUNBUFFERED 1

RUN mkdir /pandemic

WORKDIR /pandemic

ADD requirements.txt /pandemic

RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8000
ADD pandemic/ /pandemic
RUN python manage.py migrate
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
