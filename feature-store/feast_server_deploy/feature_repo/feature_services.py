from feast import FeatureService

from features import *

mnist_feature_v1 = FeatureService(
    name="mnist_feature_v1",
    features=[mnist_feature_view]
)
