import datetime, uuid
from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.future import select
from passlib.context import CryptContext
from jose import jwt, JWTError

from app.database import get_sql_db, redis_client
from app.models.user import User
from app.config import settings

pwd_ctx   = CryptContext(schemes=['bcrypt'], bcrypt__rounds=12)
router    = APIRouter(prefix='/api/auth', tags=['Auth'])
oauth2_sc = OAuth2PasswordBearer(tokenUrl='/api/auth/login')

class LoginRequest(BaseModel):
    username: str
    password: str

def create_access_token(data: dict):
    to_encode = data.copy()
    to_encode.update({
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15),
        'jti': str(uuid.uuid4())
    })
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm='HS256')

def create_refresh_token(data: dict):
    return jwt.encode({
        **data,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }, settings.REFRESH_SECRET_KEY, algorithm='HS256')

@router.post('/register')
async def register(username: str, password: str, db=Depends(get_sql_db)):
    if len(password)<8 or not any(c.isupper() for c in password) or not any(c.isdigit() for c in password):
        raise HTTPException(400, "Contraseña: ≥8 car, 1 mayúsc, 1 num")
    row = await db.execute(select(User).filter_by(username=username))
    if row.scalar_one_or_none():
        raise HTTPException(400, 'Usuario ya existe')
    user = User(username=username, password=pwd_ctx.hash(password))
    db.add(user); await db.commit()
    return {'msg':'Usuario creado'}

@router.post('/login')
async def login(request: LoginRequest, db=Depends(get_sql_db)):
    row = await db.execute(select(User).filter_by(username=request.username))
    user = row.scalar_one_or_none()
    if not user or not pwd_ctx.verify(request.password, user.password):
        raise HTTPException(401, 'Credenciales inválidas')
    return {
        'access_token':  create_access_token({'sub':request.username}),
        'refresh_token': create_refresh_token({'sub':request.username})
    }

@router.post('/refresh')
async def refresh_token(token: str = Body(..., embed=True)):
    try:
        payload  = jwt.decode(token, settings.REFRESH_SECRET_KEY, algorithms=['HS256'])
        username = payload.get('sub')
        if not username: raise JWTError()
        return {
            'access_token':  create_access_token({'sub':username}),
            'refresh_token': create_refresh_token({'sub':username})
        }
    except JWTError:
        raise HTTPException(401, 'Refresh token inválido')

@router.post('/logout')
async def logout(token: str = Depends(oauth2_sc)):
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    jti     = payload.get('jti')
    await redis_client.setex(f"blacklist:{jti}", 900, "true")
    return {'msg':'Logout successful'}

async def get_current_user(token: str = Depends(oauth2_sc)) -> str:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user    = payload.get('sub')
        if not user: raise
        return user
    except:
        raise HTTPException(401, 'Token inválido')
