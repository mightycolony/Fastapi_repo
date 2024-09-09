from fastapi import APIRouter,Depends,status,HTTPException
import schemas
from database import SessionLocal,engine
from sqlalchemy.orm import Session
import models
import oauth
import sqlite3

router = APIRouter(
    tags=['signing_key'],
    dependencies=[Depends(oauth.get_current_user)]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_pass_avail(db: Session):
    s_key = db.query(models.Sigingpass).first()
    if s_key is None or s_key.passwd == "":
        return False
    return True

@router.post("/signing_key")
def some_route(sign: schemas.signing_pass = Depends(), db: Session = Depends(get_db)):
    if not check_pass_avail(db):
        sign_key = models.Sigingpass(passwd=sign.password)
        db.add(sign_key)
        db.commit()
        db.refresh(sign_key)
        return "password added"
    return "password already exists, Kindly update if needed!"

@router.get("/signing_key_get")
def some_route(db: Session = Depends(get_db)):
    if check_pass_avail(db):
        sign_key = db.query(models.Sigingpass).first()

        return schemas.siging_pass_encrypted(password=sign_key.passwd)




