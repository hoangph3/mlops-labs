FROM hoangph3/tf_mnist_training:v0.0.1

WORKDIR /training
COPY . .

RUN pip3 install -r requirements.txt

ENTRYPOINT [ "python", "main.py" ]
