from typing import List
from fastapi import FastAPI
from odmantic import AIOEngine
from motor.motor_asyncio import AsyncIOMotorClient
import uvicorn

from model import Schema
from settings import MONGO_DATABASE, get_mongo_uri


app = FastAPI()

client = AsyncIOMotorClient(get_mongo_uri())

engine = AIOEngine(client=client, database=MONGO_DATABASE)


@app.get("/schemas", response_model=List[Schema])
async def get_schemas():
    schemas = await engine.find(Schema)
    return schemas


@app.get("/schemas/{subject}")
async def get_schema(subject: str):
    schema = await engine.find_one(Schema, Schema.subject == subject)
    return schema


@app.post("/schemas", response_model=Schema)
async def create_schema(schema: Schema):
    await engine.save(schema)
    return schema


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
