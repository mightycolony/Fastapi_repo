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
    id = Column(Integer, primary_key=True, index=True)
    passwd = Column(String)
    