from users.models import User
from users.schema import SignUp, Login,Updateprofil,PasswordResert
from fastapi import APIRouter, HTTPException, Depends, status
from database import get_db
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash, check_password_hash
from fastapi_jwt_auth2 import AuthJWT
import datetime
router = APIRouter(prefix="/users", tags=["users"])


@router.post("/signup", status_code=status.HTTP_201_CREATED)
def sign_up(user: SignUp, db: Session = Depends(get_db)):
    db_username = db.query(User).filter(User.username == user.username).first()
    if db_username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="bu Username band")

    db_email = db.query(User).filter(User.email == user.email).first()
    if db_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="bu Email band")

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
    response = {
        'status': status.HTTP_201_CREATED,
        'first_name': new_user.first_name,
        'last_name': new_user.last_name,
        'username': new_user.username,
        'email': new_user.email,
    }
    return response


@router.post("/login")
def login(data: Login, Authorize: AuthJWT = Depends()):
    db_user = data.query(User).filter(User.username == data.username).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="username yoki password xato")

    user = check_password_hash(db_user.password, data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="username yoki password xato")

    access_token = Authorize.create_access_token(subject=db_user.username,expires_time=datetime.timedelta(minutes=30))
    refresh_token = Authorize.create_refresh_token(subject=db_user.username,expires_time=datetime.timedelta(minutes=30))

    response = {
        'status': status.HTTP_200_OK,
        'access_token': access_token,
        'refresh_token': refresh_token,
    }
    return response


@router.get("/profile")
def profile(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        current_user = Authorize.get_jwt_subject()
        user = get_db().query(User).filter(User.id == current_user).first()
        return user
    except Exception as e:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.put("/update")
def update_profile(user_data: Updateprofil, Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    try:
        Authorize.jwt_required()
        current_user = Authorize.get_jwt_subject()

        user = db.query(User).filter(User.username == current_user).first()
        if not user:
            raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")

        if user_data.first_name:
            user.first_name = user_data.first_name
        if user_data.last_name:
            user.last_name = user_data.last_name
        if user_data.username:
            existing = db.query(User).filter(User.username == user_data.username).first()
            if existing and existing.id != user.id:
                raise HTTPException(status_code=400, detail="Bu username band")
            user.username = user_data.username
        if user_data.email:
            existing = db.query(User).filter(User.email == user_data.email).first()
            if existing and existing.id != user.id:
                raise HTTPException(status_code=400, detail="Bu email band")
            user.email = user_data.email

        db.commit()
        db.refresh(user)

        return {
            'status': status.HTTP_200_OK,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username,
            'email': user.email,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.put("/password-reset")
def password_reset(data: PasswordResert, Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    try:
        Authorize.jwt_required()
        current_user = Authorize.get_jwt_subject()

        user = db.query(User).filter(User.username == current_user).first()
        if not user:
            raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")

        if not check_password_hash(user.password, data.old_password):
            raise HTTPException(status_code=400, detail="Eski password xato")

        if data.new_password != data.confirm_password:
            raise HTTPException(status_code=400, detail="Yangi passwordlar mos kelmadi")

        if check_password_hash(user.password, data.new_password):
            raise HTTPException(status_code=400, detail="Yangi password eski password bilan bir xil bo'lmasligi kerak")

        user.password = generate_password_hash(data.new_password)
        db.commit()

        return {
            'status': status.HTTP_200_OK,
            'detail': "Password muvaffaqiyatli yangilandi"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


