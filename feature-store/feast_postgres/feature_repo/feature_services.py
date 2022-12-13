from feast import FeatureService
from features import mnist_fv, mnist_fresh_fv


# This groups features into a model version
mnist_feature_v1 = FeatureService(
    name="mnist_feature_v1",
    features=[
        mnist_fv,
    ],
)

mnist_feature_v2 = FeatureService(
    name="mnist_feature_v2",
    features=[
        mnist_fresh_fv,
    ],
)
