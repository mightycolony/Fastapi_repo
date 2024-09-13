from fastapi import APIRouter,Depends,status,HTTPException
from database import SessionLocal,engine
from sqlalchemy.orm import Session
import oauth
from fastapi.responses import StreamingResponse

from pre_build.build_server import Builder

router = APIRouter(
    tags=['build_init'],
    dependencies=[Depends(oauth.get_current_user)]
)
builder_init = Builder()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
      


@router.get("/build/{os_vers}")
def build_os(os_vers: str):
    return builder_init.build_init(os_vers)

@router.get("/build_init_log/{os_vers}")
def build_init_log(os_vers: str, ):
    with open(builder_init.build_init_log,'r',encoding="utf-8") as f:
            mylist = [line.rstrip('\n') for line in f]
            return StreamingResponse(mylist)
        
