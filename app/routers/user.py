from fastapi import FastAPI, Header, status, Body, Depends, APIRouter, BackgroundTasks
from fastapi.responses import JSONResponse, RedirectResponse
from typing import List
from ..db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from ..schemas import UserCreateModel, UserResponseModel, UserLoginModel, EmailModel
from ..service import UserService, TokenService, StudentService
from ..utils import create_access_token, decode_token, verify_passwd_hash, decode_safe_url
from datetime import timedelta, datetime
from ..dependencies import RefreshTokenBearer, AccessTokenBearer, get_current_user, RoleChecker,check_revoked_token
from ..errors import InvalidToken, InvalidCredentials, UserNotFound
from ..mail import create_message, mail
from ..config import settings

router = APIRouter(
    prefix="/user",
    tags=["Users"],
)

user = UserService()
revoked_token = TokenService()
student = StudentService()

role_checker = Depends(RoleChecker(['user']))
revoked_token_check = Depends(check_revoked_token)


############################################
@router.post('/send_mail')
async def send_mail(emails:EmailModel):
    emails = emails.addresses
    html = """<h1>Welcome to the App</h1>"""
    message = create_message(
        recipients=emails,
        subject='Welcome',
        body=html
    )
    await mail.send_message(message=message)
    return {"message": "Email sent successfully"}
############################################

@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=UserResponseModel)
async def create_user_account(background_tasks: BackgroundTasks, user_data: UserCreateModel = Body(...), session: AsyncSession = Depends(get_session)):
    new_user = await user.create_a_user(user_data, background_tasks, session)
    return new_user

@router.post("/login")
async def login_user(login_data: UserLoginModel = Body(...), session: AsyncSession = Depends(get_session)):
    user_email = login_data.email

    existing_user = await user.get_user_by_email(user_email, session)

    if existing_user is not None:
        passwd_valid = verify_passwd_hash(password=login_data.password, hashed_password=existing_user.password)

        if passwd_valid:
            access_token = create_access_token(user_data={
                'email': existing_user.email,
                'user_uid': str(existing_user.uid),
                'role': existing_user.role
            })
        
            refresh_token = create_access_token(user_data={
                'email': existing_user.email,
                'user_uid': str(existing_user.uid)
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
                        "email": existing_user.email,
                        'uid': str(existing_user.uid)
                    }
                }
            )
        
    raise InvalidCredentials

@router.get('/profile', dependencies=[role_checker, revoked_token_check], response_model=UserResponseModel)
async def get_user_profile(user = Depends(get_current_user)):
    return user

@router.patch('/confirm_payments', dependencies=[role_checker, revoked_token_check], response_model=UserResponseModel)
async def confirm_payment(current_user = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    result = await user.update_a_user(current_user.uid, {"is_paid": True}, session)
    return result

@router.post('/request_student_approval', dependencies=[role_checker, revoked_token_check])
async def request_student_approval(current_user = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    result = await user.request_approval( current_user.uid, current_user.exam_id, session)
    return result

@router.put('/update_user', dependencies=[role_checker, revoked_token_check], response_model=UserResponseModel)
async def update_user_profile(user_data: dict = Body(...), current_user = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    result = await user.update_a_user(current_user.uid, user_data, session)
    return result

@router.get('/get_student_result', dependencies=[role_checker, revoked_token_check])
async def get_student_result(current_user = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    result = await student.get_a_student_by_exam_id(current_user.exam_id, session)

    if result.is_approved is False:
        return JSONResponse(
            content={
                "message": "Your result is not yet approved. Please request verification"
            }
        )
    
    else:
        return result

@router.get('/refresh_token')
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):

    expiry_timestamp = token_details['exp']

    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(
            user_data=token_details['user']
        )

        return JSONResponse(
            content={
                "access_token": new_access_token
            }
        )
    
    raise InvalidToken()

@router.get("/logout")
async def logout_user(token_details: dict = Depends(AccessTokenBearer()), session: AsyncSession = Depends(get_session)):

    await revoked_token.add_token_to_blacklist(session=session, token_jti= token_details['jti'])

    return JSONResponse(
        content={
            "message": "Logout successfully"
        },
        status_code=status.HTTP_200_OK
    )

@router.get("/verify_safe_url/{url}")
async def verify_safe_url(url:str, session: AsyncSession = Depends(get_session)):
    signage = decode_safe_url(url)

    email = signage.get('email', None)
    user_uid = signage.get('user_uid', None)

    if signage is None:
        return {"message": "Invalid URL"}
    
    update_status = await user.update_a_user(user_uid, {"is_verified": True}, session)
    if update_status is None:
        raise UserNotFound
    
    return {"message": "Email verified successfully"}

@router.delete('/delete_account', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_account(current_user = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    await user.delete_a_user(current_user.uid, session)
    return JSONResponse(
        content={
            "message": "Account deleted successfully"
        }
    )