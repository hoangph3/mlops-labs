FROM jupyter/pyspark-notebook:spark-3.2.0

WORKDIR /baseimage

COPY . .

# Cache Spark packages described above.
ENV APP_PACKAGES="--master local[6] --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0,com.datastax.spark:spark-cassandra-connector_2.12:3.2.0,org.mongodb.spark:mongo-spark-connector_2.12:3.0.1,com.redislabs:spark-redis_2.12:3.0.0,org.apache.hadoop:hadoop-aws:3.2.2"
ENV PYSPARK_SUBMIT_ARGS="$APP_PACKAGES pyspark-shell"

# Submit example job
RUN spark-submit run-example $APP_PACKAGES SparkPi | true

# Pip
RUN pip3 install -r requirements.txt

# Fix h3 lib
COPY h3/out /opt/conda/lib/python3.9/site-packages/h3/out

# Update workdir
WORKDIR /home/
