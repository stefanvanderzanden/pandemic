FROM python:3.9

# Define environment variable
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /app

RUN apt update

RUN pip install --upgrade pip
RUN pip install pipenv

COPY ./Pipfile.lock /app/Pipfile.lock
COPY ./Pipfile /app/Pipfile

# TODO: Move this to Pipfile
RUN pip install django

# Install Pillow for ImageField
RUN python -m pip install Pillow

COPY ./docker/entrypoint.sh /docker-entrypoint.sh
RUN chmod 755 /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

COPY ./ /app

ENTRYPOINT ["/docker-entrypoint.sh"]
