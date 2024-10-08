from fastapi import APIRouter,Depends,status,HTTPException
import schemas
from database import SessionLocal,engine
from sqlalchemy.orm import Session
import models
import os
import oauth
from fastapi.responses import StreamingResponse
from typing import AsyncIterator
import asyncio

from pre_build.build_server import prerequisites

router = APIRouter(
    dependencies=[Depends(oauth.get_current_user)]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


####DATETIME####
import datetime
def date_time_changer(data: str):
    try:
        date_obj = datetime.datetime.strptime(data, '%Y-%m-%d')
        output_date = date_obj.strftime('%Y%m%d-%H%M%S')        
        return output_date
    except ValueError as e:
        # Handle invalid date
        raise ValueError("Invalid date format or value provided.")


##Generate DB
@router.post("/create_eol",tags=['EOL'])
def create_eol(os_data: schemas.os_info, db: Session = Depends(get_db)):
    op_date=date_time_changer(os_data.actual_eol)
    new_os_info = models.osinfo(os_name=os_data.os_name, actual_eol=os_data.actual_eol,date_eol=op_date,checksum=os_data.checksum)
    db.add(new_os_info)
    db.commit()
    db.refresh(new_os_info)
    return "os_eol_updated for {}".format(os_data.os_name)



@router.get("/eol_list", tags=['EOL'], response_model=list[schemas.os_info_all])
def get_all_eol( db: Session = Depends(get_db)):
    get_eol=db.query(models.osinfo).all()
    return get_eol
 
@router.put("/update_eol_checksum",tags=['EOL'])
def update_eol(os_data: schemas.os_info, db: Session = Depends(get_db)):  
    update_dict = os_data.model_dump(exclude_unset=True)
    existing_entry=db.query(models.osinfo).filter(models.osinfo.os_name == os_data.os_name).first()
    if existing_entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{os_data.os_name} not found in DB")  
    changes = {}
    ##Dumping new values from userinput and read it and compare it with the existing values in the db(existing_entry)
    ##and if any changes stores it in a dict (changes), if value is not "string"(default value) then no changes occurs 
    for key, new_value in update_dict.items():
            old_value = getattr(existing_entry, key, None)
            if new_value != old_value:
                changes[key] = new_value
            if changes:
                for key, value in changes.items():
                    if value != "string":
                        setattr(existing_entry, key, value)
                    if "actual_eol" in changes:
                        ##with second db query updating the eol date
                        time_stamp_changer=db.query(models.osinfo).filter(models.osinfo.os_name == os_data.os_name).first()
                        op_date=date_time_changer(time_stamp_changer.actual_eol)
                        existing_entry.date_eol=op_date
                db.commit()
    return f"OS EOL and checksum updated for {os_data.os_name}"

@router.delete("/delete_eol",tags=['EOL'])
def delete_eol(os_data: schemas.os_info_del, db: Session = Depends(get_db)):
    del_eol =  db.query(models.osinfo).filter(models.osinfo.os_name == os_data.os_name).first()
    if not del_eol:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OS not found") 
    db.delete(del_eol)
    db.commit()
    return "OS eol entry deleted {}".format(os_data.os_name)






@router.get("/prerequisites",tags=['prerequisites'])
def prerequisites_build (os_name_pre: str, db: Session = Depends(get_db)):
    builder=prerequisites(os_name_pre)
    target="Public key fingerprint:"
    table_name_key="publickey" # manual entry for models - Publickey
    data = db.query(models.osinfo).filter(models.osinfo.os_name == os_name_pre).first()
    if not os.path.exists(builder.update_server_path):
        builder.git_download()
    if os.path.exists(builder.update_server_path):
        builder.buildconf_update()
        builder.build_conf_gen(data.os_name,data.date_eol,data.checksum)
    if builder.update_server_path+"/scripts/{data.os_name}/amd64/build.conf":
        data_pass = db.query(models.Sigingpass).filter(models.Sigingpass.id == 1 ).first()
        print(builder.pexpect_log)
        if not os.path.isfile(builder.pexpect_log):
                with open(builder.pexpect_log,'w') as p:
                    pass
        print("going to write data")
        if os.path.getsize(builder.pexpect_log) == 0:
            builder.publickey_signing_gen(data_pass.passwd)
            with open(builder.pexpect_log,'r',encoding="utf-8") as f:
                mylist = [line.rstrip('\n') for line in f]
                print(mylist)
                for i,j in enumerate(mylist):
                    if target in j:
                            keyvalue=mylist[i+1]
                            checker=builder.sqlite_table_creator("check_table",table_name_key)
                            print(checker)
                            if checker == "no table":
                                    builder.sqlite_table_creator("create_table",table_name_key,keyvalue)
                            if checker == False:
                                    builder.sqlite_table_creator("add_value",table_name_key,keyvalue)
                                    return "key value added !!" 
                            else:
                                return "key already present already!"   
        else:
            return "Public Key generated already please use /public_key to get keys"    
        
@router.get('/public_key',tags=['public_key'],response_model=schemas.publickey)
def  public_key(db: Session = Depends(get_db)):
    key = db.query(models.Publickey).first()
    return key
    

