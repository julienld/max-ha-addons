from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from database import get_session
from models import Trip, TripCreate, TripRead, TripUpdate

router = APIRouter(prefix="/trips", tags=["trips"])

@router.put("/{trip_id}", response_model=TripRead)
def update_trip(trip_id: int, trip_update: TripUpdate, session: Session = Depends(get_session)):
    trip = session.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    trip_data = trip_update.dict(exclude_unset=True)
    for key, value in trip_data.items():
        setattr(trip, key, value)
        
    session.add(trip)
    session.commit()
    session.refresh(trip)
    return trip

@router.post("/", response_model=TripRead)
def create_trip(trip: TripCreate, session: Session = Depends(get_session)):
    db_trip = Trip.from_orm(trip)
    session.add(db_trip)
    session.commit()
    session.refresh(db_trip)
    return db_trip

@router.get("/", response_model=List[TripRead])
def read_trips(session: Session = Depends(get_session)):
    trips = session.exec(select(Trip)).all()
    return trips

@router.delete("/{trip_id}")
def delete_trip(trip_id: int, session: Session = Depends(get_session)):
    trip = session.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    session.delete(trip)
    session.commit()
    return {"ok": True}
