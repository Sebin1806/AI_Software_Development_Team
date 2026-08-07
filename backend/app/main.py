from fastapi import FastAPI

from app.database.database import engine, Base
from app.database import models

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Software Development Team",
    version="1.0"
)


@app.get("/")
def home():
    return {
        "message": "AI Software Development Team Backend Running"
    }