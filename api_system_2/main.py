
from fastapi import FastAPI
from sqlalchemy import text

from api_system_2.services.processor import ProcessorService
from api_system_2.models import order
from api_system_2.config.database import engine
from api_system_2.schemas.feed import FeedRequest


order.Base.metadata.create_all(bind=engine)

app = FastAPI()
process = ProcessorService()


@app.post("/execute", status_code=200)
async def execute():
    process.start()
    return {"System 2": "Running process"}


@app.post("/feed", status_code=201)
async def feed(request: FeedRequest):
    with engine.connect() as con:
        insert = ''
        for i in range(0, request.positive_inserts):
            with open("api_system_2/sql/positive_inserts.sql") as file:
                insert = insert + file.read()
        for i in range(0, request.negative_inserts):
            with open("api_system_2/sql/negative_inserts.sql") as file:
                insert = insert + file.read()
        insert = insert + 'commit;'
        con.execute(text(insert))
    return {
        'positive_inserts': request.positive_inserts,
        'negative_inserts': request.negative_inserts
    }
