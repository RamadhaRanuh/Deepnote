from sqlalchemy.orm import Session
from typing import List, Optional
from ..models import File, FileChunk

class FileRepository:
    @staticmethod
    def create_file(db: Session, filename: str, file_path: str, file_type: str, user_id: int) -> File:
        db_file = File(filename=filename, file_path=file_path, file_type=file_type, user_id=user_id)
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        return db_file
    
    @staticmethod
    def get_files(db: Session, user_id: int) -> List[File]:
        return db.query(File).filter(File.user_id == user_id).all()
    
    @staticmethod
    def get_file_by_id(db: Session, file_id: int) -> Optional[File]:
        return db.query(File).filter(File.id == file_id).first()
    
    @staticmethod
    def store_file_chunks(db: Session, file_id: int, contents: List[str]) -> List[FileChunk]:
        chunks = []
        for idx, content in enumerate(contents):
            chunk = FileChunk(content=content, chunk_index = idx, file_id=file_id)
            db.add(chunk)
            chunks.append(chunk)

        db.commit()
        for chunk in chunks:
            db.refresh(chunk)
        return chunks
    
    @staticmethod
    def delete_file(db: Session, file_id: int) -> bool:
        db_file = db.query(File).filter(File.id == file_id).first()
        if db_file:
            db.delete(db_file)
            db.commit()
            return True
        return False


