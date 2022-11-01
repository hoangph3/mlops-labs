FROM hoangph3/sk_mnist_serving:v0.0.1

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt
EXPOSE 5000

# Define environment variable
ENV MODEL_NAME SkMnist
ENV SERVICE_TYPE MODEL
ENV PERSISTENCE 0

CMD exec seldon-core-microservice $MODEL_NAME --service-type $SERVICE_TYPE
