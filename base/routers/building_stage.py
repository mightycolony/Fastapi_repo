from fastapi import APIRouter,Depends,status,HTTPException
from database import SessionLocal,engine
from sqlalchemy.orm import Session
import oauth
from fastapi.responses import StreamingResponse
import requests
import models
from pre_build.build_server import Builder

router = APIRouter(
    tags=['build_init'],
    dependencies=[Depends(oauth.get_current_user)]
)
builder_init = Builder(os_vers=None)
##loading files to chunk and aiofile for multiple io access for that file##
import aiofiles  
async def read_file_in_chunks(file_path: str):
    async with aiofiles.open(file_path, 'rb') as file:
                while True:
                   chunk = await file.read(8096)
                   print(chunk)
                   if not chunk:
                      break
                   yield chunk


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
      


@router.get("/build/{os_vers}")
def build_os(os_vers: str):
    builder_init_firstphase = Builder(os_vers)
    return builder_init_firstphase.build_init(os_vers)


@router.get("/build_init_log/{os_vers}")
async def build_init_log(os_vers: str):
    builder_init_logphase = Builder(os_vers)
    return StreamingResponse(read_file_in_chunks(builder_init_logphase.build_init_log), media_type="text/plain")

@router.get("/approve_build/{os_vers}")
def approve(os_vers: str,db: Session = Depends(get_db)):
    builder_init_approvephase = Builder(os_vers)
    data_pass = db.query(models.Sigingpass).filter(models.Sigingpass.id == 1 ).first()
    approver=builder_init_approvephase.build_approve(os_vers,data_pass.passwd)
    if approver == True:
        return "approve done!"
    else:
        return approver
        
@router.get("/upload_build/{os_vers}")
def upload_build(os_vers: str,db: Session = Depends(get_db)):
    builder_init_uploadphase = Builder(os_vers)
    data_pass2 = db.query(models.Sigingpass).filter(models.Sigingpass.id == 1 ).first()
    uploaded=builder_init.upload(os_vers,data_pass2.passwd)
    if uploaded:
        return "Build Uploaded under /home/sas/updates"
    else:
        return "nothing to upload"
        
