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

# Category
class CategoryBase(SQLModel):
    name: str
    icon: Optional[str] = None # Emoji or icon name
    parent_id: Optional[int] = Field(default=None, foreign_key="category.id")

class Category(CategoryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # Self-referencing relationship could be added but simpler to just use parent_id for now

class CategoryCreate(CategoryBase):
    pass

class CategoryRead(CategoryBase):
    id: int
