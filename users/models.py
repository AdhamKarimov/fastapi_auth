from sqlalchemy import Column, Integer, String, DateTime,Boolean
from database import Base
from datetime import datetime
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String)
    created_at = Column(DateTime,default=datetime.now)
    updated_at = Column(DateTime,default=datetime.now)
    is_staff = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    products = relationship("Products", back_populates="user")
    cart = relationship("Cart", back_populates="user", uselist=False)
    orders = relationship("Order", back_populates="user")

    def __repr__(self):
        return self.username