FROM python:3.8.0
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/
RUN chmod +x /code/infrastructure/azure/production_startup.sh
ENTRYPOINT ["/code/infrastructure/azure/production_startup.sh"]
