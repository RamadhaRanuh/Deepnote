from datetime import datetime
from fastapi import APIRouter, Depends, UploadFile, File, Form, BackgroundTasks, BaseModel
from sqlalchemy.orm import Session
from typing import List

from ...db.database import get_db
from ...controllers.files_controller import FilesController

router = APIRouter()
controller = FilesController()



class FileResponse(BaseModel):
    id: int
    type: str 
    filename: str
    file_path: str
    upload_date: datetime

    class Config:
        orm_mode = True 

class PDFRequest(BaseModel):
    file_path: str
    type: str = "pdf"
    upload_date: datetime

class URLRequest(BaseModel):
    url: str
    type: str = "url"
    upload_date: datetime

class YoutubeRequest(BaseModel):
    url: str
    type: str = "youtube"
    upload_date: datetime
    title: str



@router.post("/upload-pdf/", response_model=FileResponse)
async def process_pdf(
    request: PDFRequest,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    user_id: int = 1,
    db: Session = Depends(get_db)
):
    return await controller.process_pdf(file, background_tasks, user_id, db)
    
@router.post("/process-url/", response_model=FileResponse)
async def process_url(
    request: URLRequest,
    background_tasks: BackgroundTasks = None,
    user_id: int = 1,
    db: Session = Depends(get_db)
):
    return await controller.process_url(request, background_tasks, user_id, db)

@router.post("/process-youtube/", response_model=FileResponse)
async def process_youtube(
    request: YoutubeRequest,
    background_tasks: BackgroundTasks = None,
    user_id: int = 1,
    db: Session = Depends(get_db)
):
    return await controller.process_youtube(request, background_tasks, user_id, db)

@router.get("/", response_model=List[FileResponse])
def get_files(user_id: int = 1, db: Session = Depends(get_db)):
    return controller.get_files(user_id, db)

@router.get("/{file_id}", response_model=FileResponse)
def get_file(file_id: int, db: Session = Depends(get_db)):
    return controller.get_file(file_id, db)

@router.delete("/{file_id}")
def delete_file(file_id: int, db: Session = Depends(get_db)):
    return controller.delete_file(file_id, db)