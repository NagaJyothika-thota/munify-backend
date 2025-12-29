"""
Project Document Service - Business logic for project document operations

Handles file upload and deletion for project documents, linking files
to projects via the perdix_mp_project_documents table.
"""
from typing import Optional
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from datetime import datetime

from app.models.project_document import ProjectDocument
from app.models.project import Project
from app.services.file_service import FileService
from app.services.project_service import ProjectService
from app.core.logging import get_logger

logger = get_logger("services.project_document")


class ProjectDocumentService:
    """Service for project document operations"""
    
    # Valid document types based on frontend requirements
    VALID_DOCUMENT_TYPES = [
        "dpr",
        "feasibility_study",
        "compliance_certificate",
        "budget_approval",
        "tender_rfp",
        "project_image",  # For project images
        "optional_media"  # For optional media files
    ]
    
    def __init__(self, db: Session):
        self.db = db
        self.file_service = FileService(db)
        self.project_service = ProjectService(db)
    
    def _validate_document_type(self, document_type: str) -> None:
        """Validate document type"""
        if document_type not in self.VALID_DOCUMENT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid document_type. Must be one of: {', '.join(self.VALID_DOCUMENT_TYPES)}"
            )
    
    def _get_project_or_draft_by_reference_id(self, project_reference_id: str):
        """
        Get project or draft by reference ID.

        Returns:
            tuple[Project | None, ProjectDraft | None]:
                - (project, None) if a project exists
                - (None, draft) if only a draft exists
                - (None, None) if neither exists

        NOTE:
        -----
        This helper MUST NOT raise when nothing is found because callers
        (like upload_project_file) rely on (None, None) to decide whether
        to auto‑create a draft.
        """
        from app.models.project_draft import ProjectDraft

        # First check if project exists
        project = (
            self.db.query(Project)
            .filter(Project.project_reference_id == project_reference_id)
            .first()
        )
        if project:
            return project, None

        # If project doesn't exist, check if draft exists
        draft = (
            self.db.query(ProjectDraft)
            .filter(ProjectDraft.project_reference_id == project_reference_id)
            .first()
        )
        if draft:
            return None, draft

        # Neither exists
        return None, None
    
    def _create_draft_for_file_upload(
        self,
        project_reference_id: str,
        organization_id: str,
        uploaded_by: str
    ):
        """Auto-create a draft when file is uploaded without existing project/draft"""
        from app.models.project_draft import ProjectDraft
        from app.services.project_draft_service import ProjectDraftService
        from app.schemas.project_draft import ProjectDraftCreate
        
        logger.info(f"Auto-creating draft for file upload with project_reference_id: {project_reference_id}")
        
        draft_service = ProjectDraftService(self.db)
        
        # Create minimal draft with just project_reference_id and organization info
        draft_data = ProjectDraftCreate(
            organization_id=organization_id,
            project_reference_id=project_reference_id
        )
        
        draft = draft_service.create_draft(draft_data, user_id=uploaded_by)
        logger.info(f"Draft {draft.id} auto-created for project_reference_id {project_reference_id}")
        
        return draft
    
    def upload_project_file(
        self,
        file: UploadFile,
        project_reference_id: str,
        document_type: str,
        uploaded_by: str,
        organization_id: str,
        access_level: str = 'public',
        version: int = 1,
        created_by: Optional[str] = None,
        auto_create_draft: bool = True
    ) -> ProjectDocument:
        """
        Upload a file for a project or draft and create a project document record.
        
        Args:
            file: UploadFile object
            project_reference_id: Project reference ID (can be from project or draft)
            document_type: Document type (dpr, feasibility_study, etc.)
            uploaded_by: User ID who uploaded the file
            organization_id: Organization ID
            access_level: Access level (public, restricted, private)
            version: Document version (default: 1)
            created_by: User ID for audit trail
            auto_create_draft: If True, creates draft if project_reference_id doesn't exist
            
        Returns:
            ProjectDocument model instance
        """
        logger.info(f"Uploading project file: {document_type} for project/draft {project_reference_id}")
        
        try:
            # Validate document type
            self._validate_document_type(document_type)
            
            # Check if project or draft exists
            project, draft = self._get_project_or_draft_by_reference_id(project_reference_id)
            
            # If neither exists and auto_create_draft is True, create draft
            if not project and not draft and auto_create_draft:
                logger.info(f"Project/draft not found for {project_reference_id}, auto-creating draft")
                draft = self._create_draft_for_file_upload(
                    project_reference_id=project_reference_id,
                    organization_id=organization_id,
                    uploaded_by=uploaded_by
                )
            
            # Get organization_id from project or draft if not provided
            if not organization_id:
                if project:
                    organization_id = project.organization_id
                elif draft:
                    organization_id = draft.organization_id
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="organization_id is required when project/draft doesn't exist"
                    )
            
            # Map document_type to FileService document_type
            # For FileService, we use "Project" category
            file_service_document_type = self._map_document_type_for_file_service(document_type)
            
            # Upload file using FileService
            perdix_file = self.file_service.upload_file(
                file=file,
                organization_id=organization_id,
                uploaded_by=uploaded_by,
                file_category="Project",
                document_type=file_service_document_type,
                access_level=access_level,
                project_reference_id=project_reference_id,
                created_by=created_by or uploaded_by
            )
            
            # Create project document record
            project_document = ProjectDocument(
                project_id=project_reference_id,
                file_id=perdix_file.id,
                document_type=document_type,
                version=version,
                access_level=access_level,
                uploaded_by=uploaded_by,
                created_by=created_by or uploaded_by,
                updated_by=created_by or uploaded_by
            )
            
            self.db.add(project_document)
            self.db.commit()
            self.db.refresh(project_document)
            
            logger.info(f"Project document {project_document.id} created successfully for project {project_reference_id}")
            return project_document
            
        except HTTPException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error uploading project file: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload project file: {str(e)}"
            )
    
    def delete_project_file(
        self,
        file_id: int,
        user_id: str,
        project_reference_id: Optional[str] = None
    ) -> bool:
        """
        Delete a project file by file_id.
        
        This method:
        1. Finds the project document record by file_id
        2. Optionally validates it belongs to the specified project
        3. Deletes the project document record
        4. Soft deletes the file using FileService
        
        Args:
            file_id: File ID to delete
            user_id: User ID performing the deletion
            project_reference_id: Optional project reference ID for validation
            
        Returns:
            True if deleted successfully
        """
        logger.info(f"Deleting project file: {file_id}")
        
        try:
            # Find project document by file_id
            project_document = self.db.query(ProjectDocument).filter(
                ProjectDocument.file_id == file_id
            ).first()
            
            if not project_document:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Project document with file_id {file_id} not found"
                )
            
            # Validate project if provided
            if project_reference_id and project_document.project_id != project_reference_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File {file_id} does not belong to project {project_reference_id}"
                )
            
            # Check permission (user must be uploader)
            if project_document.uploaded_by != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to delete this file"
                )
            
            # Delete project document record
            self.db.delete(project_document)
            
            # Soft delete the file using FileService
            self.file_service.delete_file(file_id, user_id)
            
            self.db.commit()
            
            logger.info(f"Project file {file_id} deleted successfully")
            return True
            
        except HTTPException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting project file: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete project file: {str(e)}"
            )
    
    def _map_document_type_for_file_service(self, document_type: str) -> str:
        """
        Map project document type to FileService document type.
        
        FileService uses specific document types for Project category:
        - DPR
        - Project Image
        - Project videos
        
        We map our internal document types to these.
        """
        mapping = {
            "dpr": "DPR",
            "feasibility_study": "DPR",  # Map to DPR category
            "compliance_certificate": "DPR",  # Map to DPR category
            "budget_approval": "DPR",  # Map to DPR category
            "tender_rfp": "DPR",  # Map to DPR category
            "project_image": "Project Image",
            "optional_media": "Project videos"
        }
        
        return mapping.get(document_type, "DPR")  # Default to DPR if not found
    
    def get_project_documents(
        self,
        project_reference_id: str,
        document_type: Optional[str] = None
    ) -> list[ProjectDocument]:
        """
        Get all project documents for a project/draft with file details.
        
        Args:
            project_reference_id: Project reference ID
            document_type: Optional document type filter
            
        Returns:
            List of ProjectDocument instances with file relationship loaded
        """
        from app.models.perdix_file import PerdixFile
        
        # Join with perdix_mp_files to get file details
        query = (
            self.db.query(ProjectDocument)
            .join(PerdixFile, ProjectDocument.file_id == PerdixFile.id)
            .filter(
                ProjectDocument.project_id == project_reference_id,
                PerdixFile.is_deleted == False  # Only include non-deleted files
            )
        )
        
        if document_type:
            self._validate_document_type(document_type)
            query = query.filter(ProjectDocument.document_type == document_type)
        
        # Eager load file relationship
        documents = query.options(
            joinedload(ProjectDocument.file)
        ).order_by(ProjectDocument.created_at.desc()).all()
        
        return documents

