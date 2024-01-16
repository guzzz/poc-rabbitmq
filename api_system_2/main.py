
from fastapi import FastAPI
from api_system_2.models import order
from api_system_2.config.database import engine
from api_system_2.controllers import general_controller


order.Base.metadata.create_all(bind=engine)


app = FastAPI()
app.include_router(
    general_controller.router,
    prefix="/v0",
    tags=["System 2 - Orders Process"]
)
