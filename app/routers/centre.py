from fastapi import Depends, APIRouter, status
from fastapi.responses import JSONResponse
from typing import List
from ..db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from ..dependencies import RoleChecker, check_revoked_token
from..service import ExamCentreService
from ..schemas import ExamCentreCreateModel, ExamCentreResponseModel


router = APIRouter(
    prefix="/centre",
    tags=['Centre']
)

role_checker = Depends(RoleChecker(['admin', 'super_admin']))
revoked_token_check = Depends(check_revoked_token)

exam_centre = ExamCentreService()

@router.post('/create', dependencies=[role_checker, revoked_token_check])
async def create_exam_centre(exam_centre_data: ExamCentreCreateModel, session: AsyncSession = Depends(get_session)):
    result = await exam_centre.create_an_exam_centre(exam_centre_data, session=session)
    return result

@router.get('/all', dependencies=[role_checker, revoked_token_check])
async def get_all_exam_centres(session: AsyncSession = Depends(get_session)):
    result = await exam_centre.get_all_exam_centres(session=session)
    return result

@router.get('/{exam_centre_id}', dependencies=[role_checker, revoked_token_check], response_model=ExamCentreResponseModel)
async def get_exam_centre_by_exam_centre_id(exam_centre_id: str, session: AsyncSession = Depends(get_session)):
    result = await exam_centre.get_exam_centre_by_exam_centre_uid(exam_centre_id, session=session)
    return result

@router.put('/{exam_centre_id}', dependencies=[role_checker, revoked_token_check])
async def update_exam_centre(exam_centre_id: str, exam_centre_data: dict, session: AsyncSession = Depends(get_session)):
    result = await exam_centre.update_an_exam_centre(exam_centre_id, exam_centre_data, session=session)
    return result


@router.delete('/{exam_centre_id}', dependencies=[role_checker, revoked_token_check], status_code=status.HTTP_204_NO_CONTENT)
async def delete_exam_centre(exam_centre_id: str, session: AsyncSession = Depends(get_session)):
    result = await exam_centre.delete_an_exam_centre(exam_centre_id, session=session)
    return result