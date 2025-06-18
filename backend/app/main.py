from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
import time
import psycopg2
import os

from database.database import init_db, SessionLocal
from database.initial_data import create_default_users, create_demo_job
from app.api.auth import router as auth_router
from app.api.jobs import router as jobs_router
from app.api.answer import router as answers_router
from app.api.files import router as files_router
from dotenv import load_dotenv

load_dotenv()

def wait_for_db(retries=10, delay=3):
    from sqlalchemy import create_engine
    engine = create_engine(os.getenv("DATABASE_URL")) 
    for i in range(retries):
        try:
            conn = engine.connect()
            conn.close()
            print("✅ Connected to the database")
            return
        except Exception as e:
            print(f"❌ Database not ready, attempt {i + 1}/{retries}, waiting {delay}s...")
            time.sleep(delay)
    raise Exception("Failed to connect to the database after several attempts")


@asynccontextmanager
async def lifespan(app: FastAPI):
    wait_for_db()

    init_db()

    db = SessionLocal()
    create_default_users(db)
    create_demo_job(db)
    db.close()

    print("✅ Application has started.")
    yield
    print("👋 Application is shutting down...")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ["http://localhost:5173"] for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth")
app.include_router(jobs_router, prefix="/jobs")
app.include_router(answers_router, prefix="/answers")
app.include_router(files_router, prefix="/files")
