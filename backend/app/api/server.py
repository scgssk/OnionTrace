from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="OnionTrace Backend")
app.include_router(router)
