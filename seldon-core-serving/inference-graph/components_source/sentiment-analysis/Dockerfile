FROM python:3.7-slim-buster
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
EXPOSE 9000

ENV MODEL_NAME SentimentAnalysis
ENV SERVICE_TYPE MODEL
ENV PERSISTENCE 0
ENV UPGRADE_PIP_TO_LATEST 1

CMD exec seldon-core-microservice $MODEL_NAME --service-type $SERVICE_TYPE
