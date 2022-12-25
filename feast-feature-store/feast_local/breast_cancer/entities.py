from feast import (
    Entity, ValueType
)


patient = Entity(
    name="patient_id",
    value_type=ValueType.INT32,
    description="The ID of the patient"
)
