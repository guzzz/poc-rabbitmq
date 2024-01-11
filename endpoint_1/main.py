
from fastapi import FastAPI
from sqlalchemy import text

from endpoint_1.services.processor import ProcessorService
from endpoint_1.models import order
from endpoint_1.config.database import engine


order.Base.metadata.create_all(bind=engine)
with engine.connect() as con:
    with open("endpoint_1/config/load_base.sql") as file:
        query = text(file.read())
        con.execute(query)

app = FastAPI()
process = ProcessorService()

@app.get("/")
async def root():
    process.run()
    return {"message": "Hello World"}
