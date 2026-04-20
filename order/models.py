from sqlalchemy import  Column, String, Integer, Numeric,  Text, DateTime, ForeignKey
from database import Base
from datetime import datetime
from sqlalchemy.orm import relationship


class Cart(Base):
    __tablename__ = 'cart'

    id = Column(Integer, primary_key=True)
    user_id = Column( ForeignKey('users.id'),unique=True)

    items = relationship("CartItem", back_populates="cart",cascade="all, delete-orphan")
    user = relationship("User", back_populates="cart")


class CartItem(Base):
    __tablename__ = 'cart_items'

    id = Column(Integer, primary_key=True)
    cart_id = Column(ForeignKey('cart.id'))
    product_id = Column(ForeignKey('products.id'))
    quantity = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)

    cart = relationship("Cart", back_populates="items")
    product = relationship("Products")


class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('users.id'))
    total_price = Column(Numeric(10, 2))
    created_at = Column(DateTime, default=datetime.now)

    items_order = relationship("OrderItem", back_populates="order",cascade="all, delete-orphan")
    user = relationship("User", back_populates="orders")



class OrderItem(Base):
    __tablename__ = 'order_items'

    id = Column(Integer, primary_key=True)
    order_id = Column(ForeignKey('orders.id'))
    product_id = Column(ForeignKey('products.id'))
    quantity = Column(Integer)
    price = Column(Numeric(10, 2))

    order = relationship("Order", back_populates="items_order")