FROM python:3.13-rc-bookworm
RUN apt-get -y update && apt-get -y install build-essential default-mysql-client
WORKDIR /mnt
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /mnt/Emailkasten
COPY dependencies.txt /mnt/
RUN pip install --upgrade pip
RUN pip install -r dependencies.txt
COPY . /mnt/
EXPOSE 8000
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
