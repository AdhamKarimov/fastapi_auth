from fastapi import FastAPI
from fastapi_jwt_auth2 import AuthJWT

from users.router import router as user_router
from users.models import User
from database import Base, engine
from fastapi_jwt_auth2 import AuthJWT
from users.schema import Settings
from product.models import  Products
from product.urls import router as products_router
from order.models import Cart, CartItem, Order, OrderItem
from order.router import router as order_router



Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(router=products_router,prefix='/products')
app.include_router(router=order_router,prefix='/orders')


@AuthJWT.load_config
def get_config():
    return Settings()
app.include_router(user_router)

@app.get("/")
def read_root():
    return {"Hello": "World"}