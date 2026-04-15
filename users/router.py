from users.models import User
from users.schema import SignUp, Login
from fastapi import APIRouter, HTTPException, Depends, status
from database import get_db
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash, check_password_hash
from jose import jwt
from datetime import datetime, timedelta
from users.utilis import check_username_or_email

router = APIRouter(prefix="/users", tags=["users"])

SECRET_KEY = "9db9dd2b4e07c24272d2d4f84ca8238d1949b53e191786483f4c806d3b13d4c6"
ALGORITHM = "HS256"


@router.post("/signup", status_code=status.HTTP_201_CREATED)
def sign_up(user: SignUp, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="bu Username band")

    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="bu Email band")

    new_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        email=user.email,
        password=generate_password_hash(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        'status': status.HTTP_201_CREATED,
        'first_name': new_user.first_name,
        'last_name': new_user.last_name,
        'username': new_user.username,
        'email': new_user.email,
    }




@router.post("/login")
def login(data: Login, db: Session = Depends(get_db)):
    input_type = check_username_or_email(data.username_or_email)
    if input_type == 'email':
        db_user = db.query(User).filter(User.email == data.username_or_email).first()
    if input_type == 'username':
        db_user = db.query(User).filter(User.username == data.username_or_email).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="username/email yoki password xato")
    if not check_password_hash(db_user.password, data.password):
        raise HTTPException(status_code=400, detail="password xato")
    access_token = jwt.encode(
        {"sub": db_user.username, "exp": datetime.utcnow() + timedelta(minutes=30)},
        SECRET_KEY, algorithm=ALGORITHM
    )
    refresh_token = jwt.encode(
        {"sub": db_user.username, "exp": datetime.utcnow() + timedelta(days=7)},
        SECRET_KEY, algorithm=ALGORITHM
    )

    return {
        'status': status.HTTP_200_OK,
        'access_token': access_token,
        'refresh_token': refresh_token,
    }