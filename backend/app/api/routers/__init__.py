from fastapi import APIRouter
from .files_router import router as files_router
from .llm_router import router as llm_router
from .notebooks_router import router as notebook_router

# Create a main router that includes all the other routers
api_router = APIRouter()

api_router.include_router(files_router, prefix="/files", tags=["files"])
api_router.include_router(llm_router, prefix="/llm", tags=["llm"])
api_router.include_router(notebooks_router, prefix="/notebooks", taags=["notebooks"])
