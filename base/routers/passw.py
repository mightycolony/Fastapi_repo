from fastapi import APIRouter,Depends,status,HTTPException
import schemas
from database import SessionLocal,engine
from sqlalchemy.orm import Session
import models

router=APIRouter()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



async def check_pass_avail(db: Session):
    s_key = db.query(models.Sigingpass).first()
    if s_key is None or s_key.passwd == "":
        return False
    return True

@router.post("/signing_key")
def some_route(sign: schemas.signing_pass = Depends(),db: Session = Depends(get_db),dep: None = Depends(check_pass_avail)):
    sign_key = models.Sigingpass(passwd=sign.password)
    db.add(sign_key)
    db.commit()
    db.refresh(sign_key)
    return "password added"
