from dataclasses import dataclass

from pyspark.sql import DataFrame
from pyspark.sql import functions as f
from pyspark.sql.functions import udf
from pyspark.sql.types import ArrayType, FloatType, IntegerType
import numpy as np

from core import FeatureGroup


@udf(returnType=ArrayType(FloatType()))
def normalize(x: list):
    x: np.array = np.array(x)
    x = x / 255.
    return x.tolist()


@udf(returnType=ArrayType(IntegerType()))
def idx_to_onehot(y: int):
    classes = np.arange(10)
    if y not in classes:
        return
    y_true = np.zeros(10, dtype=np.int32)
    y_true[y] = 1
    return y_true.tolist()


@dataclass
class Mnist(FeatureGroup):
    name: str = "mnist"
    key: str = ""
    input_entity: str = "mnist"
    output_entity: str = "mnist"

    def transform(self, order_df: DataFrame) -> DataFrame:
        return (
            order_df
            .withColumn("feature", normalize(f.col("x")))
            .withColumn("label", idx_to_onehot(f.col("y")))
        )
