# File Storage System - Setup Guide

## ✅ Implementation Complete

The file storage system with hierarchical S3 folder structure has been successfully implemented!

## 📦 What Was Implemented

### 1. **Configuration** (`app/core/config.py`)
- Added S3 configuration settings
- Added file upload settings (max size, allowed extensions)
- Environment variable support

### 2. **Path Builder** (`app/utils/path_builder.py`)
- Type-safe enums for file categories and document types
- Builder methods for KYC, Project, and Additional categories
- Hierarchical path generation

### 3. **Storage Service** (`app/services/storage.py`)
- `S3StorageService`: Production S3 implementation
- `LocalStorageService`: Development/fallback implementation
- Unified interface with upload, download, delete, and presigned URL support

### 4. **File Service** (`app/services/file_service.py`)
- Business logic for file operations
- File validation (size, type)
- Access control
- Database integration
- Download tracking

### 5. **Schemas** (`app/schemas/file.py`)
- Request/response models
- Validation schemas

### 6. **API Endpoints** (`app/api/v1/endpoints/files.py`)
- `POST /api/v1/files/upload` - Upload file
- `GET /api/v1/files/{file_id}` - Get file metadata
- `GET /api/v1/files/{file_id}/download` - Download file
- `DELETE /api/v1/files/{file_id}` - Delete file (soft delete)
- `PATCH /api/v1/files/{file_id}/access` - Update access level
- `GET /api/v1/files/{file_id}/url` - Get presigned URL

### 7. **Dependencies** (`requirements.txt`)
- Added `boto3==1.34.0` for S3 support

## 🚀 Setup Instructions

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables

Add the following to your `.env` file:

```env
# S3 Configuration (Required for production)
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1
AWS_S3_BUCKET_NAME=your-bucket-name
AWS_S3_ENDPOINT_URL=  # Optional: for S3-compatible services (MinIO, etc.)

# Storage Type
STORAGE_TYPE=s3  # Use "local" for development without S3

# File Upload Settings
MAX_FILE_SIZE_MB=100
ALLOWED_EXTENSIONS=jpg,jpeg,png,pdf,doc,docx,xls,xlsx,mp4,avi,mov,zip
```

### Step 3: For Development (Local Storage)

If you want to test without S3, set:
```env
STORAGE_TYPE=local
```

Files will be stored in the `storage/` directory locally.

### Step 4: For Production (S3)

1. Create an S3 bucket in AWS
2. Configure IAM user with S3 access permissions
3. Set environment variables in `.env`
4. Set `STORAGE_TYPE=s3`

## 📁 Folder Structure

Files are automatically organized in S3:

```
{org_id}/
├── KYC/
│   ├── PAN/
│   └── GST/
├── Project/
│   └── {project_reference_id}/
│       ├── DPR/
│       ├── Project Image/
│       └── Project videos/
└── Additional/
    └── {project_reference_id}/
        ├── commitment/
        └── Requested document/
```

## 🔌 API Usage Examples

### Upload KYC Document (PAN)

```bash
curl -X POST "http://localhost:8000/api/v1/files/upload" \
  -H "X-User-Id: user-123" \
  -F "file=@pan_card.pdf" \
  -F "organization_id=org-123" \
  -F "file_category=KYC" \
  -F "document_type=PAN" \
  -F "access_level=private"
```

### Upload Project Document (DPR)

```bash
curl -X POST "http://localhost:8000/api/v1/files/upload" \
  -H "X-User-Id: user-123" \
  -F "file=@dpr.pdf" \
  -F "organization_id=org-123" \
  -F "file_category=Project" \
  -F "document_type=DPR" \
  -F "project_reference_id=PROJ-2024-00001" \
  -F "access_level=public"
```

### Download File

```bash
curl -X GET "http://localhost:8000/api/v1/files/123/download" \
  -H "X-User-Id: user-123" \
  -H "X-Organization-Id: org-123" \
  --output downloaded_file.pdf
```

### Get File Metadata

```bash
curl -X GET "http://localhost:8000/api/v1/files/123"
```

### Get Presigned URL

```bash
curl -X GET "http://localhost:8000/api/v1/files/123/url?expires_in=3600"
```

## 📋 Document Types

### KYC Category
- `PAN` - PAN card documents
- `GST` - GST certificate documents

### Project Category (requires project_reference_id)
- `DPR` - Detailed Project Report
- `Project Image` - Project images
- `Project videos` - Project videos

### Additional Category (requires project_reference_id)
- `commitment` - Commitment documents
- `Requested document` - Requested documents

## 🔒 Access Levels

- **private**: Only uploader and organization admins can access
- **restricted**: Organization members can access
- **public**: Anyone with file ID can access

## ⚠️ Important Notes

1. **Project Reference ID**: Required for `Project` and `Additional` categories
2. **User ID Header**: Required for upload, delete, and access update operations
3. **File Size**: Default max is 100MB (configurable)
4. **File Types**: Only allowed extensions are accepted (configurable)
5. **Soft Delete**: Files are marked as deleted but not removed from storage

## 🧪 Testing

### Test Upload (Local Storage)

1. Set `STORAGE_TYPE=local` in `.env`
2. Start the server
3. Use the upload endpoint
4. Check `storage/` directory for uploaded files

### Test Upload (S3)

1. Configure S3 credentials in `.env`
2. Set `STORAGE_TYPE=s3`
3. Start the server
4. Use the upload endpoint
5. Check S3 bucket for uploaded files

## 🐛 Troubleshooting

### S3 Connection Issues
- Verify AWS credentials are correct
- Check IAM permissions
- Verify bucket name and region
- Check if endpoint URL is needed (for MinIO, etc.)

### File Upload Fails
- Check file size (must be under MAX_FILE_SIZE_MB)
- Check file extension (must be in ALLOWED_EXTENSIONS)
- Verify project_reference_id is provided for Project/Additional categories

### Access Denied
- Check user_id header is provided
- Verify user has permission (uploader or org admin)
- Check file access_level

## 📚 Next Steps

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Configure environment**: Add S3 credentials to `.env`
3. **Test locally**: Use local storage first
4. **Test S3**: Switch to S3 storage
5. **Integrate**: Use in your application

## 🔗 Related Files

- Configuration: `app/core/config.py`
- Path Builder: `app/utils/path_builder.py`
- Storage Service: `app/services/storage.py`
- File Service: `app/services/file_service.py`
- Schemas: `app/schemas/file.py`
- Endpoints: `app/api/v1/endpoints/files.py`
- Router: `app/api/v1/api.py`

---

**The file storage system is ready to use!** 🎉

