FROM bitnami/spark:3.4.1

USER root

RUN apt-get update -y && \
    apt-get install telnet curl nano -y

RUN curl https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.231/aws-java-sdk-bundle-1.12.231.jar --output /opt/bitnami/spark/jars/aws-java-sdk-bundle-1.12.231.jar
RUN curl https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.1/hadoop-aws-3.3.1.jar --output /opt/bitnami/spark/jars/hadoop-aws-3.3.1.jar
RUN curl https://repo1.maven.org/maven2/net/java/dev/jets3t/jets3t/0.9.4/jets3t-0.9.4.jar --output /opt/bitnami/spark/jars/jets3t-0.9.4.jar

COPY requirements.txt /requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /requirements.txt
