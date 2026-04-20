from sqlalchemy import  Column, String, Integer, Numeric,  Text, DateTime, ForeignKey
from database import Base
from datetime import datetime
from sqlalchemy.orm import relationship

class Products(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    title = Column(String(20))
    desc = Column(Text, nullable=False)
    price = Column(Numeric(10, 2))
    user_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.now)
