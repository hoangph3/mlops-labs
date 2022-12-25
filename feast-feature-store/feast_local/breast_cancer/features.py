# Importing dependencies
from datetime import timedelta
from feast import Field, FeatureView
from feast.types import Float32, Int32

from entities import *
from data_sources import *


df1_fv = FeatureView(
    name="df1_feature_view",
    ttl=timedelta(seconds=86400 * 7),
    entities=[patient],
    schema=[
        Field(name="mean radius", dtype=Float32),
        Field(name="mean texture", dtype=Float32),
        Field(name="mean perimeter", dtype=Float32),
        Field(name="mean area", dtype=Float32),
        Field(name="mean smoothness", dtype=Float32)
        ],    
    source=f_source1
)

df2_fv = FeatureView(
    name="df2_feature_view",
    ttl=timedelta(seconds=86400 * 7),
    entities=[patient],
    schema=[
        Field(name="mean compactness", dtype=Float32),
        Field(name="mean concavity", dtype=Float32),
        Field(name="mean concave points", dtype=Float32),
        Field(name="mean symmetry", dtype=Float32),
        Field(name="mean fractal dimension", dtype=Float32)
        ],    
    source=f_source2
)

df3_fv = FeatureView(
    name="df3_feature_view",
    ttl=timedelta(seconds=86400 * 7),
    entities=[patient],
    schema=[
        Field(name="radius error", dtype=Float32),
        Field(name="texture error", dtype=Float32),
        Field(name="perimeter error", dtype=Float32),
        Field(name="area error", dtype=Float32),
        Field(name="smoothness error", dtype=Float32),
        Field(name="compactness error", dtype=Float32),
        Field(name="concavity error", dtype=Float32)
        ],    
    source=f_source3
)

df4_fv = FeatureView(
    name="df4_feature_view",
    ttl=timedelta(seconds=86400 * 7),
    entities=[patient],
    schema=[
        Field(name="concave points error", dtype=Float32),
        Field(name="symmetry error", dtype=Float32),
        Field(name="fractal dimension error", dtype=Float32),
        Field(name="worst radius", dtype=Float32),
        Field(name="worst texture", dtype=Float32),
        Field(name="worst perimeter", dtype=Float32),
        Field(name="worst area", dtype=Float32),
        Field(name="worst smoothness", dtype=Float32),
        Field(name="worst compactness", dtype=Float32),
        Field(name="worst concavity", dtype=Float32),
        Field(name="worst concave points", dtype=Float32),
        Field(name="worst symmetry", dtype=Float32),
        Field(name="worst fractal dimension", dtype=Float32),        
        ],    
    source=f_source4
)

target_fv = FeatureView(
    name="target_feature_view",
    entities=[patient],
    ttl=timedelta(seconds=86400 * 7),
    schema=[
        Field(name="target", dtype=Int32)        
        ],    
    source=target_source
)
