from fastapi import Depends, APIRouter, status
from fastapi.responses import JSONResponse
from typing import List
from ..db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from ..dependencies import RoleChecker
from..service import StudentService
from ..schemas import StudentCreateModel, StudentResponseModel

router = APIRouter(
    prefix="/student",
    tags=['Student']
)

role_checker = Depends(RoleChecker(['admin', 'super_admin']))

student = StudentService()


@router.post('/create', dependencies=[role_checker])
async def create_student(student_data: StudentCreateModel, session: AsyncSession = Depends(get_session)):
    result = await student.create_a_student(session, student_data)
    return result

@router.get('/all', dependencies=[role_checker], response_model=List[StudentResponseModel])
async def get_all_students(session: AsyncSession = Depends(get_session)):
    result = await student.get_all_students(session)
    return result

@router.get('/exam_id/{exam_uid}', dependencies=[Depends(RoleChecker(['user', 'admin', 'super_admin']))], response_model=StudentResponseModel)
async def get_student_by_student_uid(exam_uid: str, session: AsyncSession = Depends(get_session)):
    result = await student.get_a_student_by_exam_id(exam_uid, session)
    return result

@router.get('/{student_uid}', dependencies=[Depends(RoleChecker(['user', 'admin', 'super_admin']))])
async def get_student_by_student_uid(student_uid: str, session: AsyncSession = Depends(get_session)):
    result = await student.get_a_student(student_uid, session)
    return result

@router.put('/update/{student_uid}', dependencies=[role_checker])
async def update_student(student_uid: str, student_data: dict, session: AsyncSession = Depends(get_session)):
    result = await student.update_a_student(student_uid, student_data, session)
    return result

@router.put('/update_results/{exam_centre_no}/{subject_code}', dependencies=[role_checker])
async def update_student_results(exam_centre_no: str, subject_code: str, result_data: dict, session: AsyncSession = Depends(get_session)):
    result = await student.update_student_results(exam_centre_no, subject_code, result_data, session)
    return result

@router.delete('/delete/{student_uid}', dependencies=[role_checker], status_code=status.HTTP_204_NO_CONTENT)
async def delete_student(student_uid: str, session: AsyncSession = Depends(get_session)):
    result = await student.delete_a_student(student_uid, session)
    return result