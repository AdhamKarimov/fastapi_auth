from fastapi import FastAPI
from fastapi_jwt_auth2 import AuthJWT

from users.router import router as user_router
from users.models import User
from database import Base, engine
from fastapi_jwt_auth2 import AuthJWT
from users.schema import Settings
Base.metadata.create_all(bind=engine)

app = FastAPI()

@AuthJWT.load_config
def get_config():
    return Settings()
app.include_router(user_router)

@app.get("/")
def read_root():
    return {"Hello": "World"}