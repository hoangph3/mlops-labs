from feast import FeatureService

from features import mnist_fv, transformed_inputs, mnist_fresh_fv, transformed_fresh_inputs

# This groups features into a model version
mnist_feature_v1 = FeatureService(
    name="mnist_feature_v1",
    features=[
        mnist_fv,  # Sub-selects a feature from a feature view
        transformed_inputs,  # Selects all features from the feature view
    ],
)

mnist_feature_v2 = FeatureService(
    name="mnist_feature_v2",
    features=[
        mnist_fresh_fv,
        transformed_fresh_inputs,
    ],
)
