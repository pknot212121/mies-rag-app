from fastapi import APIRouter
from .auth import router as auth_router
from .jobs import router as jobs_router 
from .answer import router as answers_router 
from .files import router as files_router 

router = APIRouter()
router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(jobs_router, prefix="/jobs", tags=["jobs"]) 
router.include_router(answers_router, prefix="/answers", tags=["answers"]) 
router.include_router(files_router, prefix="/files", tags=["files"]) 
