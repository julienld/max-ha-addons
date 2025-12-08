from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from database import get_session
from models import Account, AccountCreate, AccountRead, User

router = APIRouter(prefix="/accounts", tags=["accounts"])

@router.post("/", response_model=AccountRead)
def create_account(account: AccountCreate, session: Session = Depends(get_session)):
    # Optional: Verify user exists if user_id is provided
    if account.user_id:
        user = session.get(User, account.user_id)
        if not user:
             raise HTTPException(status_code=404, detail="User not found")
             
    db_account = Account.model_validate(account)
    session.add(db_account)
    session.commit()
    session.refresh(db_account)
    
    # Manually populate user_name for the response if needed, or rely on relationship loading
    # For AccountRead we added user_name, let's populate it
    response = AccountRead.model_validate(db_account)
    if db_account.user:
        response.user_name = db_account.user.name
        
    return response

@router.get("/", response_model=List[AccountRead])
def read_accounts(session: Session = Depends(get_session)):
    accounts = session.exec(select(Account)).all()
    results = []
    for account in accounts:
        # Enriched model with user_name
        acc_read = AccountRead.model_validate(account)
        if account.user:
            acc_read.user_name = account.user.name
        results.append(acc_read)
    return results

@router.delete("/{account_id}")
def delete_account(account_id: int, session: Session = Depends(get_session)):
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    session.delete(account)
    session.commit()
    return {"ok": True}

@router.put("/{account_id}", response_model=AccountRead)
def update_account(account_id: int, account_data: AccountCreate, session: Session = Depends(get_session)):
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if account_data.user_id:
        user = session.get(User, account_data.user_id)
        if not user:
             raise HTTPException(status_code=404, detail="User not found")
             
    account.name = account_data.name
    account.user_id = account_data.user_id
    session.add(account)
    session.commit()
    session.refresh(account)
    
    response = AccountRead.model_validate(account)
    if account.user:
        response.user_name = account.user.name
        
    return response
