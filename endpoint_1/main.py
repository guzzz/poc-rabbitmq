
from fastapi import FastAPI

from endpoint_1.services.processor import ProcessorService
from endpoint_1.models import order
from endpoint_1.config.database import engine


order.Base.metadata.create_all(bind=engine)

app = FastAPI()
process = ProcessorService()

@app.get("/")
async def root():
    process.run()
    return {"message": "Hello World"}
