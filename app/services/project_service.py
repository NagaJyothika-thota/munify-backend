from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.project import Project as ProjectModel
from app.models.user import User as UserModel
from app.models.party import Party as PartyModel
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.core.logging import get_logger
from app.utils.logger import log_business_event, log_error, log_database_operation
from fastapi import HTTPException, status

logger = get_logger("services.project")


class ProjectService:
    def __init__(self, db: Session):
        self.db = db

    def _validate_municipal_user(self, user_id: int) -> UserModel:
        """Validate that user exists and has MUNICIPAL party type"""
        logger.info(f"Validating municipal user: {user_id}")
        user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            logger.error(f"User not found: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if not user.party_id:
            logger.error(f"User {user_id} has no party association")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="User must be associated with a party"
            )
        
        party = self.db.query(PartyModel).filter(PartyModel.id == user.party_id).first()
        if not party or party.type != "MUNICIPAL":
            logger.error(f"User {user_id} party type is not MUNICIPAL: {party.type if party else 'No party'}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only municipal users can create projects"
            )
        
        logger.info(f"User {user_id} validated as municipal")
        return user

    def _calculate_funding_gap(self, funding_required: float, funds_secured: float = 0) -> float:
        """Calculate funding gap"""
        return funding_required - funds_secured

    def create_project(self, user_id: int, project_data: ProjectCreate) -> ProjectModel:
        """Create a new project for municipal user"""
        log_business_event(
            "project_creation_started",
            user_id=user_id,
            entity_type="project",
            project_title=project_data.project_title,
            project_category=project_data.project_category
        )
        
        try:
            # Validate user is municipal
            user = self._validate_municipal_user(user_id)
            
            # Calculate funding gap
            funding_gap = self._calculate_funding_gap(
                project_data.funding_required,
                project_data.funds_secured or 0
            )
            
            # Create project
            project = ProjectModel(
                user_id=user_id,
                project_title=project_data.project_title,
                project_category=project_data.project_category,
                project_stage=project_data.project_stage,
                description=project_data.description,
                location=project_data.location,
                start_date=project_data.start_date,
                end_date=project_data.end_date,
                total_project_cost=project_data.total_project_cost,
                funding_required=project_data.funding_required,
                funds_secured=project_data.funds_secured or 0,
                funding_gap=funding_gap,
                media=project_data.media,
                disclosures_summary=project_data.disclosures_summary,
                admin_validation_checklist=project_data.admin_validation_checklist,
                status=project_data.status or "draft",
                notes=project_data.notes,\
                municipality_id=project_data.municipality_id
            )
            
            log_database_operation("create", "projects", user_id=user_id)
            self.db.add(project)
            self.db.commit()
            self.db.refresh(project)
            
            log_business_event(
                "project_created",
                user_id=user_id,
                entity_type="project",
                entity_id=project.id,
                project_title=project.project_title
            )
            
            return project
        except Exception as e:
            log_error(
                "project_creation_failed",
                str(e),
                user_id=user_id,
                project_title=project_data.project_title
            )
            self.db.rollback()
            raise

    def get_project_by_id(self, project_id: int) -> ProjectModel:
        """Get project by ID"""
        project = self.db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        return project

    def get_project_by_user(self, user_id: int) -> ProjectModel:
        """Get project by user ID"""
        project = self.db.query(ProjectModel).filter(ProjectModel.user_id == user_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found for user"
            )
        return project

    def update_project_by_id(self, project_id: int, project_data: ProjectUpdate) -> ProjectModel:
        """Update project by ID"""
        # Get existing project
        project = self.get_project_by_id(project_id)
        
        # Validate user is municipal
        self._validate_municipal_user(project.user_id)
        
        # Update fields
        update_data = project_data.dict(exclude_unset=True)
        
        # Recalculate funding gap if financial fields are updated
        if any(field in update_data for field in ['funding_required', 'funds_secured']):
            funding_required = update_data.get('funding_required', project.funding_required)
            funds_secured = update_data.get('funds_secured', project.funds_secured)
            update_data['funding_gap'] = self._calculate_funding_gap(funding_required, funds_secured)
        
        for field, value in update_data.items():
            setattr(project, field, value)
        
        self.db.commit()
        self.db.refresh(project)
        return project

    def update_project(self, user_id: int, project_data: ProjectUpdate) -> ProjectModel:
        """Update project for municipal user"""
        # Validate user is municipal
        self._validate_municipal_user(user_id)
        
        # Get existing project
        project = self.get_project_by_user(user_id)
        
        # Update fields
        update_data = project_data.dict(exclude_unset=True)
        
        # Recalculate funding gap if financial fields are updated
        if any(field in update_data for field in ['funding_required', 'funds_secured']):
            funding_required = update_data.get('funding_required', project.funding_required)
            funds_secured = update_data.get('funds_secured', project.funds_secured)
            update_data['funding_gap'] = self._calculate_funding_gap(funding_required, funds_secured)
        
        for field, value in update_data.items():
            setattr(project, field, value)
        
        self.db.commit()
        self.db.refresh(project)
        return project

    def delete_project_by_id(self, project_id: int) -> bool:
        """Delete project by ID"""
        # Get existing project
        project = self.get_project_by_id(project_id)
        
        # Validate user is municipal
        self._validate_municipal_user(project.user_id)
        
        self.db.delete(project)
        self.db.commit()
        return True

    def delete_project(self, user_id: int) -> bool:
        """Delete project for municipal user"""
        # Validate user is municipal
        self._validate_municipal_user(user_id)
        
        # Get existing project
        project = self.get_project_by_user(user_id)
        
        self.db.delete(project)
        self.db.commit()
        return True

    def get_all_projects(self, skip: int = 0, limit: int = 100, status_filter: str = None):
        """Get all projects with optional status filter"""
        query = self.db.query(ProjectModel)
        
        if status_filter:
            query = query.filter(ProjectModel.status == status_filter)
        
        total = query.count()
        projects = query.offset(skip).limit(limit).all()
        
        return {
            "projects": projects,
            "total": total
        }
