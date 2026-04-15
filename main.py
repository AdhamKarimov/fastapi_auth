from fastapi import FastAPI
from users.router import router as user_router
from users.models import User
from database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(user_router)

@app.get("/")
def read_root():
    return {"Hello": "World"}