FROM python:3.7-slim-buster

WORKDIR /app

COPY model.pkl .
COPY Model.py .
COPY Dockerfile .

CMD ["python", "Model.py"]