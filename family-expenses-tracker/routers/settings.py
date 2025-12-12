from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from database import get_session
from models import Setting, SettingCreate, SettingRead

router = APIRouter(prefix="/settings", tags=["settings"])

@router.get("/", response_model=List[SettingRead])
def read_settings(session: Session = Depends(get_session)):
    settings = session.exec(select(Setting)).all()
    return settings

@router.put("/{key}", response_model=SettingRead)
def update_setting(key: str, setting: SettingCreate, session: Session = Depends(get_session)):
    db_setting = session.get(Setting, key)
    if not db_setting:
        # Create if not exists
        db_setting = Setting(key=key, value=setting.value)
        session.add(db_setting)
    else:
        db_setting.value = setting.value
        session.add(db_setting)
        
    session.commit()
    session.refresh(db_setting)
    return db_setting
