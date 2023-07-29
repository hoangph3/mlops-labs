
db = db.getSiblingDB('registry')

db.schema.insert(
    {
        "subject": "entity-mnist",
        "type": "entity",
        "name": "mnist",
        "key": "",
        "properties": {
            "type": "struct",
            "fields": [
                {
                    "name": "x",
                    "type": {"type": "array", 'elementType': "float", "containsNull": true},
                    "nullable": true,
                    "metadata": {}
                },
                {
                    "name": "y",
                    "type": "integer",
                    "nullable": true,
                    "metadata": {}
                },
                {
                    "name": "timestamp",
                    "type": "string",
                    "nullable": true,
                    "metadata": {}
                }
            ]
        }
    }
)
