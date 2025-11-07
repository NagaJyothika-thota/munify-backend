from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.project import Project, ProjectCreate, ProjectUpdate
from app.services.project_service import ProjectService

router = APIRouter()


@router.get("/{project_id}", response_model=Project, status_code=status.HTTP_200_OK)
def get_project(project_id: int, db: Session = Depends(get_db)):
    """Get project by ID"""
    service = ProjectService(db)
    return service.get_project_by_id(project_id)


@router.post("/", response_model=Project, status_code=status.HTTP_201_CREATED)
def create_project(project_data: ProjectCreate, db: Session = Depends(get_db)):
    """Create project for municipal user"""
    service = ProjectService(db)
    return service.create_project(project_data.user_id, project_data)


@router.put("/{project_id}", response_model=Project, status_code=status.HTTP_200_OK)
def update_project(project_id: int, project_data: ProjectUpdate, db: Session = Depends(get_db)):
    """Update project by ID"""
    service = ProjectService(db)
    return service.update_project_by_id(project_id, project_data)


@router.delete("/{project_id}", status_code=status.HTTP_200_OK)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """Delete project by ID"""
    service = ProjectService(db)
    service.delete_project_by_id(project_id)
    return {"status": "success", "message": "Project deleted successfully"}


@router.get("/", status_code=status.HTTP_200_OK)
def get_all_projects(
    skip: int = 0,
    limit: int = 100,
    status_filter: str = None,
    db: Session = Depends(get_db)
):
    """Get all projects with optional filtering"""
    service = ProjectService(db)
    result = service.get_all_projects(skip, limit, status_filter)
    
    return {
        "status": "success",
        "message": "Projects fetched successfully",
        "data": result["projects"],
        "total": result["total"]
    }