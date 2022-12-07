from feast import (
    Entity, ValueType
)


event_id = Entity(
    name="id",
    value_type=ValueType.INT32,
    description="The ID of the event"
)
