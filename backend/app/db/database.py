from sqlalchemy import Column, Integer, Boolean, Float, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key = True, index = True)
    email = Column(String, unique=True, index = True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default = datetime.now)

    files = relationship("File", back_populates="owner")
    notebooks = relationship("Notebook", back_populates="owner")

class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_keys=True, index=True)
    filename = Column(String, index = True)
    file_path = Column(String)
    file_type = Column(String) 
    upload_date = Column(DateTime, default=datetime.now)
    user_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="files")

class FileChunk(Base):
    __tablename__ = "file_chunks"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    embedding = Column(Text, nullable = True)
    chunk_index = Column(Integer)
    file_id = Column(Integer, ForeignKey("files.id"))

    file = relationship("File", back_populates = "chunks")

class Notebook(Base):
    __tablename__ = "notebooks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    user_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="notebooks")
    entries = relationship("NotebookEntry", back_populates="notebook")

class NotebookEntry(Base):
    __tablename__ = "notebook_entries"

    id = Column(Integer, primary_key = True, index = True)
    content = Column(Text)
    entry_type = Column(String) # "text", "query", "response"
    created_at = Column(DateTime, default=datetime.now)
    notebook_id = Column(Integer, ForeignKey("notebooks.id"))

    notebook = relationship("Notebook", back_populates="entries")