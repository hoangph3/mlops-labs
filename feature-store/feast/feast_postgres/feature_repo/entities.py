from feast import Entity


event_id = Entity(
    name="event_id",
    join_keys=["event_id"],
    description="event id"
)
