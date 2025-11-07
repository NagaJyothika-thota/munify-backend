import logging
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.commitment import Commitment as CommitmentModel
from app.models.project import Project as ProjectModel
from app.models.user import User as UserModel
from app.models.party import Party as PartyModel
from app.schemas.commitment import CommitmentCreate, CommitmentUpdate
from app.core.logging import get_logger
from app.utils.logger import log_business_event, log_error, log_database_operation
from fastapi import HTTPException, status

logger = get_logger("services.commitment")


class CommitmentService:
    def __init__(self, db: Session):
        self.db = db

    def _validate_buyer_user(self, user_id: int) -> UserModel:
        """Validate that user exists and has BUYER party type"""
        log_business_event("user_validation_started", user_id=user_id, entity_type="user")
        
        user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            log_error("user_not_found", f"User not found: {user_id}", user_id=user_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if not user.party_id:
            log_error("user_no_party", f"User has no associated party: {user_id}", user_id=user_id)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User must be associated with a party"
            )
        
        party = self.db.query(PartyModel).filter(PartyModel.id == user.party_id).first()
        if not party or party.type != "BUYER":
            log_error("user_not_buyer", f"User party type is not BUYER: {user_id}, party_type: {party.type if party else 'None'}", user_id=user_id)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only BUYER type parties can make commitments"
            )
        
        log_business_event("user_validated_as_buyer", user_id=user_id, entity_type="user")
        return user

    def _validate_commitment_amount(self, project_id: int, amount: Decimal) -> ProjectModel:
        """Validate that commitment amount doesn't exceed funding gap"""
        log_business_event("amount_validation_started", project_id=project_id, amount=amount, entity_type="project")
        
        project = self.db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
        if not project:
            log_error("project_not_found", f"Project not found: {project_id}", project_id=project_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Use Decimal directly for consistent comparison
        funding_gap = project.funding_gap or Decimal('0')
        
        if amount > funding_gap:
            log_error("amount_exceeds_gap", f"Commitment amount {amount} exceeds funding gap {funding_gap}", 
                     project_id=project_id, amount=amount, funding_gap=funding_gap)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Commitment amount ({amount}) cannot exceed funding gap ({funding_gap})"
            )
        
        log_business_event("amount_validated", project_id=project_id, amount=amount, funding_gap=funding_gap, entity_type="project")
        return project

    def _update_project_financials(self, project_id: int, commitment_amount: Decimal, operation: str = "add"):
        """Update project's funds_secured and funding_gap after commitment changes"""
        log_business_event("project_financials_update_started", project_id=project_id, 
                          amount=commitment_amount, operation=operation, entity_type="project")
        
        project = self.db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
        if not project:
            log_error("project_not_found_for_update", f"Project not found for financial update: {project_id}", project_id=project_id)
            return
        
        # Use Decimal directly for consistent arithmetic
        current_funds_secured = project.funds_secured or Decimal('0')
        funding_required = project.funding_required or Decimal('0')
        
        if operation == "add":
            project.funds_secured = current_funds_secured + commitment_amount
        elif operation == "subtract":
            project.funds_secured = max(Decimal('0'), current_funds_secured - commitment_amount)
        
        # Recalculate funding gap
        total_active_commitments = self.db.query(func.coalesce(func.sum(CommitmentModel.amount), 0)).filter(
            CommitmentModel.project_id == project_id,
            CommitmentModel.status == "ACTIVE",
        ).scalar()
        
        total_commitments = Decimal(str(total_active_commitments)) if total_active_commitments else Decimal('0')
        project.funding_gap = funding_required  -  project.funds_secured 
        
        log_database_operation("update", "projects", project_id=project_id, 
                              funds_secured=float(project.funds_secured), funding_gap=float(project.funding_gap))
        
        log_business_event("project_financials_updated", project_id=project_id, 
                          funds_secured=float(project.funds_secured), funding_gap=float(project.funding_gap), entity_type="project")

    def create_commitment(self, commitment_data: CommitmentCreate) -> CommitmentModel:
        """Create a new commitment with full validation and project updates"""
        log_business_event("commitment_creation_started", 
                          user_id=commitment_data.user_id, 
                          project_id=commitment_data.project_id,
                          amount=commitment_data.amount,
                          entity_type="commitment")
        
        try:
            # Validate user is a BUYER
            user = self._validate_buyer_user(commitment_data.user_id)
            
            # Validate commitment amount doesn't exceed funding gap
            project = self._validate_commitment_amount(commitment_data.project_id, commitment_data.amount)
            
            # Validate party exists and matches user's party
            party = self.db.query(PartyModel).filter(PartyModel.id == commitment_data.party_id).first()
            if not party:
                log_error("party_not_found", f"Party not found: {commitment_data.party_id}", party_id=commitment_data.party_id)
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Party not found"
                )
            
            if party.id != user.party_id:
                log_error("party_mismatch", f"Commitment party {commitment_data.party_id} doesn't match user party {user.party_id}", 
                         user_id=commitment_data.user_id, commitment_party_id=commitment_data.party_id, user_party_id=user.party_id)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Commitment party must match user's party"
                )
            
            # Create commitment
            db_commitment = CommitmentModel(**commitment_data.dict())
            log_database_operation("create", "commitments", 
                                  user_id=commitment_data.user_id, 
                                  project_id=commitment_data.project_id,
                                  amount=commitment_data.amount)
            
            self.db.add(db_commitment)
            self.db.commit()
            self.db.refresh(db_commitment)
            
            # Update project financials
            self._update_project_financials(commitment_data.project_id, commitment_data.amount, "add")
            self.db.commit()
            
            log_business_event("commitment_created", 
                              commitment_id=db_commitment.id,
                              user_id=commitment_data.user_id, 
                              project_id=commitment_data.project_id,
                              amount=commitment_data.amount,
                              entity_type="commitment")
            
            return db_commitment
            
        except HTTPException:
            raise
        except Exception as e:
            log_error("commitment_creation_failed", str(e), 
                     user_id=commitment_data.user_id, 
                     project_id=commitment_data.project_id,
                     amount=commitment_data.amount)
            self.db.rollback()
            raise

    def get_commitment_by_id(self, commitment_id: int) -> CommitmentModel:
        """Get a commitment by ID"""
        log_business_event("commitment_fetch_started", commitment_id=commitment_id, entity_type="commitment")
        
        commitment = self.db.query(CommitmentModel).filter(CommitmentModel.id == commitment_id).first()
        if not commitment:
            log_error("commitment_not_found", f"Commitment not found: {commitment_id}", commitment_id=commitment_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Commitment not found"
            )
        
        log_business_event("commitment_fetched", commitment_id=commitment_id, entity_type="commitment")
        return commitment

    def get_commitments_by_project(self, project_id: int, skip: int = 0, limit: int = 100):
        """Get all commitments for a project with pagination"""
        log_business_event("project_commitments_fetch_started", project_id=project_id, skip=skip, limit=limit, entity_type="commitment")
        
        query = self.db.query(CommitmentModel).filter(CommitmentModel.project_id == project_id)
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        
        log_business_event("project_commitments_fetched", project_id=project_id, total=total, count=len(items), entity_type="commitment")
        return {"items": items, "total": total}

    def update_commitment(self, commitment_id: int, commitment_data: CommitmentUpdate) -> CommitmentModel:
        """Update an existing commitment"""
        log_business_event("commitment_update_started", commitment_id=commitment_id, entity_type="commitment")
        
        try:
            db_commitment = self.get_commitment_by_id(commitment_id)
            old_amount = db_commitment.amount
            
            # Validate new amount if provided
            if commitment_data.amount is not None:
                if commitment_data.amount <= 0:
                    log_error("invalid_amount", f"Invalid commitment amount: {commitment_data.amount}", commitment_id=commitment_id)
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail="Commitment amount must be positive"
                    )
                
                # Check if new amount exceeds funding gap (considering current commitment)
                project = self.db.query(ProjectModel).filter(ProjectModel.id == db_commitment.project_id).first()
                current_gap = (project.funding_gap or Decimal('0')) + old_amount  # Add back current commitment amount
                if commitment_data.amount > current_gap:
                    log_error("amount_exceeds_gap", f"New commitment amount {commitment_data.amount} exceeds available gap {current_gap}", 
                             commitment_id=commitment_id, new_amount=commitment_data.amount, available_gap=current_gap)
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"New commitment amount ({commitment_data.amount}) cannot exceed available funding gap ({current_gap})"
                    )
            
            # Update commitment
            update_data = commitment_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_commitment, field, value)
            
            log_database_operation("update", "commitments", commitment_id=commitment_id, **update_data)
            self.db.commit()
            
            # Update project financials if amount changed
            if commitment_data.amount is not None and commitment_data.amount != old_amount:
                amount_diff = commitment_data.amount - old_amount
                self._update_project_financials(db_commitment.project_id, abs(amount_diff), 
                                              "add" if amount_diff > 0 else "subtract")
                self.db.commit()
            
            self.db.refresh(db_commitment)
            
            log_business_event("commitment_updated", commitment_id=commitment_id, entity_type="commitment")
            return db_commitment
            
        except HTTPException:
            raise
        except Exception as e:
            log_error("commitment_update_failed", str(e), commitment_id=commitment_id)
            self.db.rollback()
            raise

    def delete_commitment(self, commitment_id: int) -> None:
        """Delete a commitment and update project financials"""
        log_business_event("commitment_deletion_started", commitment_id=commitment_id, entity_type="commitment")
        
        try:
            db_commitment = self.get_commitment_by_id(commitment_id)
            project_id = db_commitment.project_id
            amount = db_commitment.amount
            
            # Delete commitment
            log_database_operation("delete", "commitments", commitment_id=commitment_id, project_id=project_id, amount=amount)
            self.db.delete(db_commitment)
            self.db.commit()
            
            # Update project financials
            self._update_project_financials(project_id, amount, "subtract")
            self.db.commit()
            
            log_business_event("commitment_deleted", commitment_id=commitment_id, project_id=project_id, amount=amount, entity_type="commitment")
            
        except HTTPException:
            raise
        except Exception as e:
            log_error("commitment_deletion_failed", str(e), commitment_id=commitment_id)
            self.db.rollback()
            raise
