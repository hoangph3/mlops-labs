FROM hoangph3/spark-py:feature-store

WORKDIR /app

COPY . .
RUN pip install -r requirements.txt

ENTRYPOINT ["python3", "main.py"]
