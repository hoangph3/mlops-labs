FROM apache/airflow:2.6.3-python3.8

USER root

# Install OpenJDK-11
RUN apt-get update -y && \
    apt-get install git openjdk-11-jdk ant -y

# Set JAVA_HOME
ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-amd64/
RUN export JAVA_HOME

USER airflow

COPY requirements.txt /requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /requirements.txt
