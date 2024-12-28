from fastapi import FastAPI, APIRouter
import logging
from contextlib import asynccontextmanager
from .db.main import init_db, get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from .routers import admin, centre, student, user, subject
from .service import AdminService
from .errors import register_all_errors
from .middleware import register_middleware


@asynccontextmanager
async def life_span(app:FastAPI):
    print(f"Server is starting...")
    await init_db()
    yield
    print(f"Server has been stopped")

version = "v1"

app = FastAPI(
    title="Resultify",
    description="A Result Verification System",
    version=version,
    lifespan=life_span
)

register_all_errors(app)
register_middleware(app)


api_router = APIRouter()
api_router.include_router(admin.router)
api_router.include_router(centre.router)
api_router.include_router(student.router)
api_router.include_router(user.router)
api_router.include_router(subject.router)


app.include_router(api_router, prefix=f"/api/{version}")


@app.get('/')
async def read_root():
    return {"message": "Welcome to Resultify"}



