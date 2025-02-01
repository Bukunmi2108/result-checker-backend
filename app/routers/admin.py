from fastapi import FastAPI, Header, status, Body, Depends, APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List
from ..db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from ..schemas import AdminLoginModel, AdminProfileModel, EmailModel, AdminCreateModel
from ..service import AdminService, TokenService, UserService, ExamCentreService, StudentService
from ..utils import create_access_token, verify_passwd_hash
from datetime import timedelta, datetime
from ..dependencies import AccessTokenBearer, get_current_admin, RoleChecker, check_revoked_token
from ..errors import InvalidCredentials
from ..mail import create_message, mail
from typing import List

router = APIRouter(
    prefix="/admin",
    tags=['Admin']
)


admin = AdminService()
user = UserService()
exam_centre = ExamCentreService()
student = StudentService()
revoked_token = TokenService()
role_checker = Depends(RoleChecker(['admin', 'super_admin']))
revoked_token_check = Depends(check_revoked_token)



@router.post('/send_mail')
async def send_mail(emails:EmailModel):
    try:
        emails = emails.addresses
        html = """<h1>Welcome to the App</h1>"""
        message = create_message(
            recipients=emails,
            subject='Welcome',
            body=html
        )
        await mail.send_message(message=message)
        return {"message": "Email sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#####
@router.post('/create_super_admin')
async def create_super_admin(background_tasks: BackgroundTasks, session: AsyncSession = Depends(get_session)):
    result = await admin.create_super_admin( background_tasks, session=session)
    
    return result

#####

@router.post("/login")
async def login_admin(login_data: AdminLoginModel = Body(...), session: AsyncSession = Depends(get_session)):
    admin_email = login_data.email

    existing_admin = await admin.get_admin_by_email(admin_email, session=session)
    if existing_admin is not None:
        passwd_valid = verify_passwd_hash(password=login_data.password, hashed_password=existing_admin.password)

        if passwd_valid:
            access_token = create_access_token(user_data={
                'email': existing_admin.email,
                'user_uid': str(existing_admin.uid),
                'role': existing_admin.role
            })
        
            refresh_token = create_access_token(user_data={
                'email': existing_admin.email,
                'user_uid': str(existing_admin.uid)
            },
            refresh=True,
            expiry=timedelta(days=2)
            )


            return JSONResponse(
                content={
                    "message": "Login successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {
                        "email": existing_admin.email,
                        'uid': str(existing_admin.uid)
                    }
                }
            )
        
    raise InvalidCredentials

@router.get('/profile', dependencies=[role_checker, revoked_token_check], response_model=AdminProfileModel)
async def get_user_profile(user = Depends(get_current_admin)):
    return user

@router.get('/all', dependencies=[role_checker, revoked_token_check], response_model=List[AdminProfileModel])
async def get_user_profile(user = Depends(get_current_admin), session: AsyncSession = Depends(get_session)):
    admins = await admin.get_all_admins(session=session)
    return admins

@router.post('/create/admin', dependencies=[role_checker, revoked_token_check], response_model=AdminProfileModel)
async def create_an_admin(background_tasks: BackgroundTasks, admin_data: AdminCreateModel = Body(...), user = Depends(get_current_admin), session: AsyncSession = Depends(get_session)):
    res = await admin.create_an_admin(background_tasks=background_tasks, admin_data=admin_data, session=session)
    return res

################################################
####################GET COUNT###################
@router.get('/get_all_users', dependencies=[role_checker, revoked_token_check])
async def get_all_users(session: AsyncSession = Depends(get_session)):
    users = await user.get_all_users(session)
    user_count = len(users)
    return user_count

@router.get('/get_all_centres', dependencies=[role_checker, revoked_token_check])
async def get_all_centres(session: AsyncSession = Depends(get_session)):
    centres = await exam_centre.get_all_exam_centres(session)
    centre_count = len(centres)
    return centre_count

@router.get('/get_all_students', dependencies=[role_checker, revoked_token_check])
async def get_all_students(session: AsyncSession = Depends(get_session)):
    students = await student.get_all_students(session)
    student_count = len(students)
    return student_count
####################GET COUNT#########################
######################################################

@router.get("/logout")
async def logout_user(token_details: dict = Depends(AccessTokenBearer()), session: AsyncSession = Depends(get_session)):

    await revoked_token.add_token_to_blacklist(session=session, token_jti= token_details['jti'])

    return JSONResponse(
        content={
            "message": "Logout successfully"
        },
        status_code=status.HTTP_200_OK
    )