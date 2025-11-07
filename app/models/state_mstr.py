from app.core.database import Base
from sqlalchemy import Column, Integer, String

class UserMstr(Base):
    __tablename__ = "state_mstr"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(Integer, unique=True, nullable=False)
    value = Column(String(100), nullable=False)