from fastapi import Depends,HTTPException,Query
from sqlalchemy.orm import Session
from product.schemas import ProductCreate, ProductOut, ProductUpdate
from product.models import Products

from database import get_db
from fastapi import APIRouter
from product.crud import product_create,get_products,get_product,search_products,update_product,delete_product
router = APIRouter()


@router.post("/add",response_model=ProductOut,)
def create_product(data: ProductCreate,db: Session = Depends(get_db)):
    return  product_create(db,data)

@router.get("/list",response_model=list[ProductOut])
def list_products(db: Session = Depends(get_db)):
    return  get_products(db)


@router.get("/{product_id}",response_model=ProductOut)
def list_get_product(product_id: int,db: Session = Depends(get_db)):
    product = get_product(db,product_id)
    if not product:
        raise HTTPException(status_code=404,detail="Not found")
    return product


@router.get("/search", response_model=list[ProductOut])
def search_product(query: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    results = search_products(db, query)
    if not results:
        raise HTTPException(status_code=404, detail="Hech narsa topilmadi")
    return results


@router.put("/{product_id}", response_model=ProductOut)
def edit_product(product_id: int, data: ProductUpdate, db: Session = Depends(get_db)):
    product = update_product(db, product_id, data)
    if not product:
        raise HTTPException(status_code=404, detail="Not found")
    return product


@router.delete("/{product_id}")
def ochirish_product(product_id: int, db: Session = Depends(get_db)):
    product = delete_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Not found")
    return {"message": f"Mahsulot o'chirildi", "id": product_id}