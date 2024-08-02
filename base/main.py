from fastapi import FastAPI,HTTPException
from  database import engine,SessionLocal
import models
from routers import osinfo,passw
from sqlalchemy.orm import Session


app=FastAPI()
models.Base.metadata.create_all(bind=engine)
app.include_router(osinfo.router)




