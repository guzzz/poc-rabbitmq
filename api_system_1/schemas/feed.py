
from pydantic import BaseModel


class FeedRequest(BaseModel):
    positive_inserts: int
    negative_inserts: int
