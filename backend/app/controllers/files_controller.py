from fastapi import UploadFile, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
import os
import shutil
from uuid import uuid4
import logging

from ..services.file_service import DocumentProcessor
from ..db.repositories.file_repository import FileRepository

logger = logging.getLogger(__name__)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Background processing class
class process_in_background:
    def __init__(self, file_type, file_path, file_id, db):
        self.file_type = file_type
        self.file_path = file_path
        self.file_id = file_id
        self.db = db
        self.processor = DocumentProcessor()
        
    def process(self):
        documents = self.processor.process_documents(self.file_path, self.file_type)
        if not documents:
            logger.error(f"Error processing file: {self.file_path}")
            return
        contents = [doc.page_content for doc in documents]
        FileRepository.store_file_chunks(self.db, self.file_id, contents)


class FilesController:
    def __init__(self):
        self.processor = process_in_background()
        
    async def process_pdf(self, request, background_tasks, user_id, db):
        """Handle PDF File Upload"""
        logger.info(f"Processing PDF: {request.filename} for user: {user_id}")
        # Generate unique filename to prevent collisions
        file_extension = os.path.splitext(request.filename)[1]
        unique_filename = f"{uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Validate file type
        file_type = "pdf" if file_extension.lower() == ".pdf" else "unknown"
        if file_type == "unknown":
            raise HTTPException(status_code=400, detail="Unsupported file type")
            
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(request.file, buffer)
        
        # Save file record in database
        try:
            db_file = FileRepository.create_file(
                db,
                filename=request.filename,
                file_path=file_path, 
                file_type=file_type,
                user_id=user_id
            )
        except Exception as e:
            # Clean up the file if database operation fails
            if os.path.exists(file_path):
                os.remove(file_path)
            logger.error(f"Database error saving file: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
            
        # Process document using service
        self.processor(
            db, file_type, file_path, db_file.id, background_tasks
        )
        
        return db_file
    
    async def process_url(self, request, background_tasks, user_id, db):
        """Handle URL Processing"""
        logger.info(f"Uploading file: {request.url} for user: {user_id}")
        # Create file record
        try:
            db_file = FileRepository.create_file(
                db,
                filename=f"URL: {request.url[:50]}...",
                file_path=request.url,
                file_type="url",
                user_id=user_id
            )
        except Exception as e:
            logger.error(f"Databse error saving file: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
            
        # Process URL using service
        self.processor(
            db, "url", request.url, db_file.id, background_tasks
        )
        
        return db_file
        
    async def process_youtube(self, request, background_tasks, user_id, db):
        """Handle YouTube Processing"""
        logger.info(f"Processing Youtube: {request.url} for user: {user_id}")
        # Similar implementation as process_url with youtube type
        try:
            db_file = FileRepository.create_file(
                db,
                filename=f"YouTube: {request.title or request.url}",
                file_path=request.url,
                file_type="youtube",
                user_id=user_id
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
            
        # Process YouTube using service
        self.processor(
            db, "youtube", request.url, db_file.id, background_tasks
        )
        
        return db_file
    
    def get_files(self, user_id, db):
        """Get all files for a user"""
        logger.info(f"Getting files for user: {user_id}")
        files = FileRepository.get_files(db, user_id)
        return files
        
    def get_file(self, file_id, db):
        """Get a single file by ID"""
        logger.info(f"Getting file: {file_id}")
        file = FileRepository.get_file_by_id(db, file_id)
        if not file:
            raise HTTPException(status_code=404, detail="File not found")
        return file
        
    def delete_file(self, file_id, db):
        """Delete File"""
        logger.info(f"Deleting file: {file_id}")
        file = FileRepository.get_file_by_id(db, file_id)
        if not file:
            logger.warning(f"File not found: {file_id}")
            raise HTTPException(status_code=404, detail="File not found")
            
        # Delete physical file if it's a PDF
        if file.file_type == "pdf" and os.path.exists(file.file_path):
            try:
                os.remove(file.file_path)
            except Exception as e:
                # Log but continue with database deletion
                logger.error(f"Error deleting file: {str(e)}")
                
        # Delete from database
        success = FileRepository.delete_file(db, file_id)
        if not success:
            logger.error(f"Failed to delete file from database: {file_id}")
            raise HTTPException(status_code=500, detail="Failed to delete file")
            
        logger.info(f"File deleted successfully: {file_id}")
        return {"message": "File deleted successfully"}