from fastapi import Depends, APIRouter, status
from fastapi.responses import JSONResponse
from typing import List
from ..db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from ..dependencies import RoleChecker
from..service import SubjectService
from ..schemas import SubjectCreateModel, SubjectResponseModel

router = APIRouter(
    prefix="/subject",
    tags=['Subjects']
)

role_checker = Depends(RoleChecker(['admin', 'super_admin']))

subject = SubjectService()

@router.post("/create", dependencies=[role_checker], status_code=status.HTTP_201_CREATED)
async def create_subject(subject_data: SubjectCreateModel, session: AsyncSession = Depends(get_session)):
    new_subject = await subject.create_a_subject(subject_data, session)
    return new_subject

@router.get("/all", dependencies=[role_checker], response_model=List[SubjectResponseModel])
async def get_all_subjects(session: AsyncSession = Depends(get_session)):
    all_subjects = await subject.get_all_subjects(session)
    return all_subjects

@router.get("/{subject_code}", dependencies=[role_checker])
async def get_subject_by_code(subject_code: str, session: AsyncSession = Depends(get_session)):
    subject = await subject.get_subject_by_code(subject_code, session)
    return subject

@router.put("/{subject_uid}", dependencies=[role_checker])
async def update_subject(subject_uid: str, subject_data: SubjectCreateModel, session: AsyncSession = Depends(get_session)):
    updated_subject = await subject.update_a_subject(subject_uid, subject_data, session)
    return updated_subject

@router.delete("/{subject_uid}", dependencies=[role_checker])
async def delete_subject(subject_uid: str, session: AsyncSession = Depends(get_session)):
    deleted_subject = await subject.delete_a_subject(subject_uid, session)
    return deleted_subject