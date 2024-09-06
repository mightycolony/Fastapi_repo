from fastapi import APIRouter,Depends,status,HTTPException
import schemas
from database import SessionLocal,engine
from sqlalchemy.orm import Session
import models
import os
from hashing import bcrypt,get_password_hash
from pre_build.build_server import prerequisites
import oauth

router = APIRouter(
    tags=['User_Creation'],
    dependencies=[Depends(oauth.get_current_user)]
)

builder=prerequisites()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.put("/create_user")
def create_user (userdata: schemas.userdata, db: Session = Depends(get_db)):
    new_user = models.User(username=userdata.username,password = bcrypt(userdata.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return "useradd: {}".format(userdata.username)

@router.get("/get_password_user/{user}")
def get_password (user: str, db: Session = Depends(get_db)):
    data_pass = db.query(models.User).filter(models.User.username == user).first()
    return { "pass": data_pass.password }

