from sqlalchemy.orm import Session
from sqlalchemy import or_
from product.models import Products
from product.schemas import ProductOut,ProductCreate,ProductUpdate


def product_create(db: Session, data: ProductCreate):
    product = Products(**data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def get_products(db:Session,):
    return  db.query(Products).all()


def get_product(db:Session,product_id: int):
    return  db.query(Products).filter(Products.id == product_id).first()


def search_products(db: Session, query: str):
    return db.query(Products).filter(
        or_(
            Products.title.ilike(f"%{query}%"),
            Products.desc.ilike(f"%{query}%"),
        )
    ).all()


def delete_product(db: Session, product_id: int):
    product = db.query(Products).filter(Products.id == product_id).first()
    if not product:
        return None

    db.delete(product)
    db.commit()
    return product


def update_product(db: Session, product_id: int, data: ProductUpdate):
    product = db.query(Products).filter(Products.id == product_id).first()
    if not product:
        return None

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)
    return product