
from pydantic import BaseModel


class InsertDataRequest(BaseModel):
    positive_inserts: int
    negative_inserts: int
