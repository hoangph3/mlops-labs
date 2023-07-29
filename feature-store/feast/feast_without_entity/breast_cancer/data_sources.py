from feast import FileSource


f_source1 = FileSource(
    name="df1_file_source",
    path="data/data_df1.parquet",
    timestamp_field="event_timestamp",
    description="A table describing the source of the first set of features",
    owner="test1@gmail.com"
)

f_source2 = FileSource(
    name="df2_file_source",
    path="data/data_df2.parquet",
    timestamp_field="event_timestamp",
    description="A table describing the source of the second set of features",
    owner="test2@gmail.com"
)

f_source3 = FileSource(
    name="df3_file_source",
    path="data/data_df3.parquet",
    timestamp_field="event_timestamp",
    description="A table describing the source of the third set of features",
    owner="test3@gmail.com"
)

f_source4 = FileSource(
    name="df4_file_source",
    path="data/data_df4.parquet",
    timestamp_field="event_timestamp",
    description="A table describing the source of the fourth set of features",
    owner="test4@gmail.com"
)

target_source = FileSource(
    name="target_file_source",
    path="data/target_df.parquet", 
    timestamp_field="event_timestamp",
    description="A table describing the source of the targets (labels)",
    owner="test@gmail.com"
)
