
from fastapi import APIRouter
from sqlalchemy import text

from api_system_2.services.processor import ProcessorService
from api_system_2.config.database import engine
from api_system_2.schemas.insert_data import InsertDataRequest


router = APIRouter()
process = ProcessorService()


@router.post("/insert-data", status_code=201)
async def fill_database(request: InsertDataRequest):
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

@router.post("/process/run", status_code=200)
async def execute_process():
    process.start()
    return {"System 2": "Running process"}

@router.post("/process/clear", status_code=200)
async def clear_process_info():
    process.clear()
    return {"System 2": "Process cleared"}

@router.post("/process/unblock", status_code=200)
async def unblock_status_error():
    process.unblock()
    return {"System 2": "Process unblocked"}
