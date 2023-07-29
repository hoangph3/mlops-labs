from loguru import logger
from pyspark.sql import SparkSession

import catalog
import settings
from core import FeatureGroupJob


def spark_session(app_name: str) -> SparkSession:
    return (
        SparkSession
        .builder
        .appName(app_name)
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.0.1")
        .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:3.0.1")
        .config("spark.mongodb.input.uri", settings.get_mongo_uri())
        .config("spark.mongodb.output.uri", settings.get_mongo_uri())
        .getOrCreate()
    )


def start_transformation_jobs():
    spark = spark_session("Transformations")

    for feature_group in catalog.feature_groups:
        logger.info(f"Starting transformation {feature_group}")
        FeatureGroupJob(spark, feature_group).run()

    spark.streams.awaitAnyTermination()


if __name__ == "__main__":
    start_transformation_jobs()
