FROM hoangph3/sk_mnist_training:v0.0.1

WORKDIR /training
COPY . .
RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "main.py" ]
