from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship

# User (Family Member)
class UserBase(SQLModel):
    name: str = Field(index=True)

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    accounts: List["Account"] = Relationship(back_populates="user")

class UserCreate(UserBase):
    pass

class UserRead(UserBase):
    id: int

# Account
class AccountBase(SQLModel):
    name: str
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")

class Account(AccountBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    user: Optional[User] = Relationship(back_populates="accounts")

class AccountCreate(AccountBase):
    pass

class AccountRead(AccountBase):
    id: int
    user_name: Optional[str] = None # Enriched field
