FROM python:3.8-slim

# Copy app handler code
COPY kafka_demo/kafka_demo.py kafka_demo.py
COPY feature_repo/data/mnist.npz .

# Install dependencies
COPY kafka_demo/requirements.txt .
RUN pip3 install -r requirements.txt

CMD [ "python", "-u", "kafka_demo.py", "--mode", "setup", "--bootstrap_servers", "broker:29092"]
