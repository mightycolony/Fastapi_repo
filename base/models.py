from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class osinfo(Base):
    __tablename__ = "osinfo"
    id = Column(Integer, primary_key=True, index=True)
    os_name = Column(String)
    actual_eol = Column(Integer)
    date_eol = Column(Integer)  
    checksum = Column(String)
    
class Sigingpass(Base):
    __tablename__ = "signingpass"
    id = Column(Integer, primary_key=True, index=True,)
    passwd = Column(String)

class Publickey(Base):
    __tablename__ = "publickey"
    id = Column(Integer, primary_key=True, index=True,)
    pub_key = Column(String)
    
class User(Base):
    __tablename__ = "userdata"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    password = Column(String)

