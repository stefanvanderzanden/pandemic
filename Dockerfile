FROM 3.6-jessie
ENV PYTHONUNBUFFERED 1

RUN mkdir /pandemic

WORKDIR /pandemic

ADD requirements.txt /pandemic

RUN pip install -r requirements.txt

ADD pandemic/ /pandemic

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
