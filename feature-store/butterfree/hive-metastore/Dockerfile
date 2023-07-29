FROM openjdk:8u242-jre

WORKDIR /opt

ENV HADOOP_VERSION=3.2.2
ENV METASTORE_VERSION=3.0.0

ENV JAVA_HOME=/usr/local/openjdk-8
ENV HADOOP_HOME=/opt/hadoop-${HADOOP_VERSION}
ENV HIVE_HOME=/opt/apache-hive-${METASTORE_VERSION}-bin

ENV HADOOP_CLASSPATH=${HADOOP_HOME}/share/hadoop/tools/lib/aws-java-sdk-bundle-1.11.563.jar:${HADOOP_HOME}/share/hadoop/tools/lib/hadoop-aws-3.2.2.jar

COPY . .
COPY conf/hive-site.xml ${HIVE_HOME}/conf
COPY scripts/entrypoint.sh /entrypoint.sh

RUN apt-get update -y && apt-get install procps -y

# RUN curl -L https://apache.org/dist/hive/hive-${METASTORE_VERSION}/apache-hive-${METASTORE_VERSION}-bin.tar.gz | tar zxf - && \
    # curl -L https://archive.apache.org/dist/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz | tar zxf - && \
    # curl -L https://dev.mysql.com/get/Downloads/Connector-J/mysql-connector-java-8.0.19.tar.gz | tar zxf - 

RUN tar zxf apache-hive-${METASTORE_VERSION}-bin.tar.gz && \
    tar zxf hadoop-${HADOOP_VERSION}.tar.gz && \
    tar zxf mysql-connector-java-8.0.19.tar.gz && \
    cp mysql-connector-java-8.0.19/mysql-connector-java-8.0.19.jar ${HIVE_HOME}/lib/ && \
    rm ${HIVE_HOME}/lib/guava-19.0.jar && \
    cp ${HADOOP_HOME}/share/hadoop/hdfs/lib/guava-27.0-jre.jar ${HIVE_HOME}/lib/ && \
    rm -rf *.tar.gz && \
    chmod +x /entrypoint.sh

EXPOSE 9083

ENTRYPOINT ["sh", "-c", "/entrypoint.sh"]
