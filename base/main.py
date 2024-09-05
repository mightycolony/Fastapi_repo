from fastapi import FastAPI,HTTPException
from  database import engine,SessionLocal
import models
from routers import osinfo,passw,userinfo
from sqlalchemy.orm import Session


app=FastAPI()
models.Base.metadata.create_all(bind=engine)
app.include_router(osinfo.router)
app.include_router(userinfo.router)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def include_routers(app: FastAPI, db: Session):
    if passw.check_pass_avail(db) == True:
        app.include_router(passw.router)
    else:
        print("Router not included due to condition")

db = next(get_db())  
include_routers(app, db)

"""
next(): This function retrieves the next item from an iterator or generator. 
If get_db() is a generator (as shown above), next(get_db()) gets the first item yielded by get_db(), which is a Session instance.
"""