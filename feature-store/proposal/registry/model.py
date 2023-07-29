from odmantic import Model


class Schema(Model):
    subject: str
    type: str
    name: str
    key: str
    properties: dict
