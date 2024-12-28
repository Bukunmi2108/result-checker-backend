from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from typing import List
from .db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from .utils import decode_token
from .service import UserService, AdminService, TokenService
from .errors import (AccessDenied, AccessTokenRequired, InvalidToken, RefreshTokenRequired, RevokedToken)

user_service = UserService()
admin_service = AdminService()
token_service = TokenService()


class TokenBearer(HTTPBearer):
    
    def __init__(self, auto_error = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)

        token = creds.credentials

        token_data = decode_token(token)

        if not self.token_valid(token):
            raise InvalidToken()


        self.verify_token_data(token_data)
        
        return token_data
    
    def token_valid(self, token:str) -> bool:

        token_data = decode_token(token)

        return True if token_data is not None else False
    
    def verify_token_data(self, token_data):
        raise NotImplementedError("Please Override this method in child classes")

class AccessTokenBearer(TokenBearer):
    
    def verify_token_data(self, token_data:dict) -> None:
        if token_data and token_data['refresh']:
            raise AccessTokenRequired()


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data:dict) -> None:
        if token_data and not token_data['refresh']:
            raise RefreshTokenRequired()

async def get_current_user(token_details: dict = Depends(AccessTokenBearer()), session: AsyncSession = Depends(get_session)):
    user_email = token_details['user']['email']

    user = await user_service.get_user_by_email(email=user_email, session=session)

    return user

async def get_current_admin(token_details: dict = Depends(AccessTokenBearer()), session: AsyncSession = Depends(get_session)):
    admin_email = token_details['user']['email']
    admin = await admin_service.get_admin_by_email(email=admin_email, session=session)
    return admin

class RoleChecker:
    def __init__(self,allowed_roles:List[str] ) -> None:

        self.allowed_roles = allowed_roles

    def __call__(self, current_user = Depends(get_current_user), current_admin = Depends(get_current_admin)):
        if current_user is not None and current_user.role in self.allowed_roles:
            return True
        if current_admin is not None and current_admin.role in self.allowed_roles:
                return True
        raise AccessDenied()

async def check_revoked_token(token_details: dict = Depends(AccessTokenBearer()), session: AsyncSession = Depends(get_session)):

    token_jti = token_details['jti']
    is_blacklisted = await token_service.get_token_from_blacklist(session, token_jti)
    if is_blacklisted:
        raise RevokedToken()
    return True