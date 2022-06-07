FROM openjdk:8-jre
ENV SPARK_VERSION=3.2.1
ENV SPARK_DIR=/opt/spark
ENV PATH $SPARK_DIR/bin:$SPARK_DIR/sbin:$PATH

ADD setup/spark-${SPARK_VERSION}-bin-hadoop3.2.tgz /opt
RUN apt-get update && apt-get -y install bash 
RUN apt-get -y install python3=3.9

RUN mv /opt/spark-${SPARK_VERSION}-bin-hadoop3.2 ${SPARK_DIR}

ADD spark-local/setup-master/spark-env.sh ${SPARK_DIR}/conf
ADD spark-local/setup-master/start.sh ${SPARK_DIR}/bin

ADD dataset /opt/tap/spark/dataset
# Add Python Code
ADD code/*  /opt/tap/
# Add Java Code
ADD apps /opt/tap/apps

# master port
EXPOSE 7077
# web ui
EXPOSE 8080

WORKDIR ${SPARK_DIR}
ENTRYPOINT [ "start.sh"]
