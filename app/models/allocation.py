from sqlalchemy import Column, Integer, Numeric, ForeignKey, String
from sqlalchemy.orm import relationship
from app.core.database import Base


class Allocation(Base):
    __tablename__ = "allocations"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    buyer_party_id = Column(Integer, ForeignKey("parties.id"), nullable=False)
    amount = Column(Numeric(18, 2), nullable=False)
    notes = Column(String(255))

    # Relationships
    project = relationship("Project", back_populates="allocations")


