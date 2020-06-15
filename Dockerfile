FROM joyzoursky/python-chromedriver:3.6-alpine3.7-selenium

WORKDIR /app

COPY ./* /app/

RUN pip install -r requirements.txt

ENTRYPOINT ["python","netflix.py"]
