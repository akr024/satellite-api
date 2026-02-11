from fastapi import FastAPI
from app.routers import satellite

app = FastAPI()

app.include_router(satellite.router)