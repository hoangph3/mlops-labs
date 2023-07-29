from pyspark.sql import SparkSession


def init_spark():
    sql = SparkSession.builder\
        .appName("example")\
        .config("spark.jars", "/opt/spark/examples/postgresql-42.5.1.jar")\
        .getOrCreate()
    sc = sql.sparkContext
    return sql, sc


def main():
    url = "jdbc:postgresql://my-postgres:5432/my_db"
    properties = {
        "user": "admin",
        "password": "secret",
        "driver": "org.postgresql.Driver"
    }
    file = "/opt/spark/examples/starbucks.csv"
    sql, sc = init_spark()

    df = sql.read.load(file,format = "csv", inferSchema="true", sep=",", header="true")
    df.show()

    # transform
    return (
        df
        .withColumn("sale_price", df.price*0.9)
        .write.jdbc(url=url, table="starbucks", mode='append', properties=properties)
    )


if __name__ == '__main__':
    main()
