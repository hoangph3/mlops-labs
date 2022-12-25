from feast import FeatureService

from features import *

feature_service_v1 = FeatureService(
    name="feature_v1",
    features=[df1_fv]
)

feature_service_v2 = FeatureService(
    name="feature_v2",
    features=[df1_fv, df2_fv]
)

feature_service_v3 = FeatureService(
    name="feature_v3",
    features=[df1_fv, df2_fv, df3_fv]
)

feature_service_v4 = FeatureService(
    name="feature_v4",
    features=[df1_fv, df2_fv, df3_fv, df4_fv]
)
