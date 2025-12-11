from sqlalchemy import Column, BigInteger, String, ForeignKey, Text, Integer
from sqlalchemy.dialects.postgresql import TIMESTAMP, JSONB
from sqlalchemy.sql import func
from sqlalchemy import text
from app.core.database import Base


class Dummy(Base):
    __tablename__ = "dummy_table"

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(255), nullable=False)
    age = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)



    # Audit fields
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=True)
    created_by = Column(String(255), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True)
    updated_by = Column(String(255), nullable=True)


