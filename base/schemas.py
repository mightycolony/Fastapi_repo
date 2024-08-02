from pydantic import BaseModel,field_validator
from typing import Optional
from datetime import datetime,date
import re


class os_info(BaseModel):
    os_name: Optional[str] = None
    actual_eol: Optional[str] = None
    checksum: Optional[str] = None
    
    @field_validator('checksum')
    def checksum_validator(cls,c):
        has_only_digit = any(char.isdigit() for char in c)
        has_only_alpha = any(char.isalpha() for char in c)
        if c == "string":
            return c
        if not has_only_digit or not has_only_alpha:
                raise ValueError('checksum must be alphanumeric')
        return c

        
            
        
    @field_validator('os_name')
    def os_name_validator(cls,m):
        pattern_os = r'^\d{1,2}\.\d{1,2}-RELEASE$'
        if re.match(pattern_os, m):
            return m
        else:
            raise ValueError('OS Name must be in the format for example: 13.1-RELEASE')
    @field_validator('actual_eol')
    def date_validator(cls, v):
        v=str(v)
        pattern_str = r'^\d{4}-\d{2}-\d{2}$'
        if v == "string" or re.match(pattern_str, v):
            return v
        raise ValueError('Date must be in the format YYYY-DD-MM')





class os_info_del(BaseModel):
    os_name: str
    

class os_info_all(BaseModel):
    os_name: str
    actual_eol: str
    checksum: str


class signing_pass(BaseModel):
    password: str
    