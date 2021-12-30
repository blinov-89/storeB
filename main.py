from typing import List
import databases
import sqlalchemy
from fastapi import FastAPI
from pydantic import BaseModel


DATABASE_URL = "sqlite:///./store.db"

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

store = sqlalchemy.Table(
    "store",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.INTEGER, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column("count", sqlalchemy.INTEGER),
    sqlalchemy.Column("manufacture", sqlalchemy.String),
    sqlalchemy.Column("price", sqlalchemy.FLOAT),
    sqlalchemy.Column("size", sqlalchemy.FLOAT),
)

engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

metadata.create_all(engine)

#получение данных от пользователя
class ItemIn(BaseModel):
    name: str
    count: int
    manufacture: str
    price: float
    size: float

#модель того как хранятся данные в базе данных
class Item(BaseModel):
    id: int
    name: str
    count: int
    manufacture: str
    price: float
    size: float

app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get('/item/', response_model=List[Item])
async def read_items():
    query = store.select()
    return await database.fetch_all(query)


@app.post("/item/", response_model=Item)
async def create_item(item: ItemIn):
    query = store.insert().values(name=item.name,
                                  count=item.count,
                                  manufacture=item.manufacture,
                                  price=item.price,
                                  size=item.size
                                  )
    last_record_id = await database.execute(query)
    return {**item.dict(), "id": last_record_id}


@app.delete("/item/{item_id}")
async def delete_item(item_id: int):
    query = store.delete().where(store.c.id == item_id)
    await database.execute(query)
    return {"detail": "Item deleted"}
