from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from order.schemas import OrderBase
from fastapi_jwt_auth2 import AuthJWT
from fastapi_jwt_auth2.exceptions import AuthJWTException
from users.models import User
from product.models import Products
from order.models import Cart, CartItem,Order,OrderItem

router = APIRouter()


@router.post("/add_cart", status_code=status.HTTP_201_CREATED)
def add_to_cart(order: OrderBase,db: Session = Depends(get_db),Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        current_user_id = Authorize.get_jwt_subject()
    except AuthJWTException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token yaroqsiz yoki muddati o'tgan"
        )

    if order.quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Miqdor 0 dan katta bo'lishi kerak"
        )

    user = db.query(User).filter(User.id == current_user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Foydalanuvchi topilmadi"
        )

    product = db.query(Products).filter(Products.id == order.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mahsulot topilmadi"
        )

    if product.stock < order.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Yetarli mahsulot yo'q. Mavjud: {product.stock} ta"
        )

    try:
        cart = user.cart
        if not cart:
            cart = Cart(user_id=user.id)
            db.add(cart)
            db.flush()

        cart_item = db.query(CartItem).filter(
            CartItem.cart_id == cart.id,
            CartItem.product_id == order.product_id
        ).first()

        if cart_item:
            if cart_item.quantity + order.quantity > product.stock:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Savatchadagi miqdor zaxiradan oshib ketadi. Mavjud: {product.stock} ta"
                )
            cart_item.quantity += order.quantity
        else:
            cart_item = CartItem(
                cart_id=cart.id,
                product_id=order.product_id,
                quantity=order.quantity
            )
            db.add(cart_item)

        db.commit()
        db.refresh(cart_item)

        return {
            "message": "Mahsulot savatchaga qo'shildi",
            "cart_id": cart.id,
            "product": product.title,
            "quantity": cart_item.quantity,
            "mavjud_zaxira": product.stock - cart_item.quantity
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Serverda xatolik yuz berdi"
        )


@router.post("/checkout", status_code=status.HTTP_201_CREATED)
def checkout(
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends()
):
    try:
        Authorize.jwt_required()
        current_user_id = Authorize.get_jwt_subject()
    except AuthJWTException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token yaroqsiz yoki muddati o'tgan"
        )

    user = db.query(User).filter(User.id == current_user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Foydalanuvchi topilmadi"
        )

    cart = user.cart
    if not cart or not cart.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Savatcha bo'sh"
        )

    try:
        total_price = 0
        order_items = []

        for cart_item in cart.items:
            product = cart_item.product

            if product.stock < cart_item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"'{product.title}' mahsuloti yetarli emas. Mavjud: {product.stock} ta"
                )

            item_price = product.price * cart_item.quantity
            total_price += item_price

            order_items.append({
                "product": product,
                "quantity": cart_item.quantity,
                "price": item_price
            })

        order = Order(
            user_id=user.id,
            total_price=total_price
        )
        db.add(order)
        db.flush()

        for item in order_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item["product"].id,
                quantity=item["quantity"],
                price=item["price"]
            )
            db.add(order_item)

            item["product"].stock -= item["quantity"]

        for cart_item in cart.items:
            db.delete(cart_item)

        db.commit()
        db.refresh(order)

        return {
            "message": "Buyurtma muvaffaqiyatli yaratildi",
            "order_id": order.id,
            "total_price": float(order.total_price),
            "items": [
                {
                    "product": item["product"].title,
                    "quantity": item["quantity"],
                    "price": float(item["price"])
                }
                for item in order_items
            ],
            "created_at": order.created_at
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Serverda xatolik yuz berdi"
        )



@router.get("/my_orders", status_code=status.HTTP_200_OK)
def get_my_orders(
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends()
):
    try:
        Authorize.jwt_required()
        current_user_id = Authorize.get_jwt_subject()
    except AuthJWTException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token yaroqsiz yoki muddati o'tgan"
        )

    orders = db.query(Order).filter(Order.user_id == current_user_id).all()

    if not orders:
        return {"message": "Hali buyurtmalar yo'q", "orders": []}

    return {
        "orders": [
            {
                "order_id": order.id,
                "total_price": float(order.total_price),
                "created_at": order.created_at,
                "items": [
                    {
                        "product_id": item.product_id,
                        "quantity": item.quantity,
                        "price": float(item.price)
                    }
                    for item in order.items_order
                ]
            }
            for order in orders
        ]
    }