from typing import Any, Callable
from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse

class ResultifyException(Exception):
    """This is the base class for all bookly errors."""
    pass

class InvalidToken(ResultifyException):
    """User has provided an invalid or expired token"""
    pass

class InvalidCredentials(ResultifyException):
    """User has provided Invalid Email or Password"""
    pass

class RevokedToken(ResultifyException):
    """User Token has been revoked, login for access"""
    pass

class AccessTokenRequired(ResultifyException):
    """User has provided a Refresh Token where Access Token is required"""
    pass

class RefreshTokenRequired(ResultifyException):
    """User has provided a Access Token where Refresh Token is required"""
    pass

class AccessDenied(ResultifyException):
    """User does not have the necessary permissions to perform operation"""
    pass

class UserAlreadyExists(ResultifyException):
    """User has provided an email for a user who already exists during signup"""
    pass

class StudentAlreadyExists(ResultifyException):
    """User has provided an email for a user who already exists during signup"""
    pass

class BookNotFound(ResultifyException):
    """Book Not Found"""
    pass

class TagNotFound(ResultifyException):
    """Tag Not Found"""
    pass

class UserNotFound(ResultifyException):
    """User Not Found"""
    pass

class StudentNotFound(ResultifyException):
    """Student Not Found"""
    pass

class CentreNotFound(ResultifyException):
    """Center Not Found"""
    pass

class RequestNotFound(ResultifyException):
    """Request Not Found"""
    pass

class ExamIdNotFound(ResultifyException):
    """Exam Id Not Found"""
    pass

class CenterNoNotFound(ResultifyException):
    """Center No. Not Found"""
    pass

class CentreAlreadyExists(ResultifyException):
    """Center No. can not be duplicate"""
    pass

class AdminAlreadyExists(ResultifyException):
    """Admin already exists"""
    pass

class SubjectNotFound(ResultifyException):
    """Subject Not Found"""
    pass

class SubjectAlreadyExists(ResultifyException):
    """Subject already exists"""
    pass


def create_exception_handler(status_code:int, initial_detail: Any) -> Callable[[Request, Exception], JSONResponse]:
    async def exception_handler(request: Request, exc: ResultifyException):
        return JSONResponse(
            content=initial_detail,
            status_code=status_code
        )
    
    return exception_handler 

def register_all_errors (app: FastAPI):
    app.add_exception_handler(
        UserNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "User is not found",
                "error": "Not Found"
            }
        )
    )
    app.add_exception_handler(
        CentreNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Centre is not found",
                "error": "Not Found"
            }
        )
    )
    app.add_exception_handler(
        RequestNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Verification Request is not found",
                "error": "Not Found"
            }
        )
    )
    app.add_exception_handler(
        StudentNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Student is not found",
                "error": "Not Found"
            }
        )
    )
    app.add_exception_handler(
        ExamIdNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Exam Id is Incorrect",
                "error": "Not Found"
            }
        )
    )
    app.add_exception_handler(
        CenterNoNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Center No is Incorrect",
                "error": "Not Found"
            }
        )
    )
    app.add_exception_handler(
        SubjectNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Subject Code is Incorrect",
                "error": "Not Found"
            }
        )
    )
    app.add_exception_handler(
        CentreAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "Center No. already exists",
                "error": "Duplicate"
            }
        )
    )
    app.add_exception_handler(
        SubjectAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "Subject already exists",
                "error": "Duplicate"
            }
        )
    )
    app.add_exception_handler(
        AdminAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "Admin already exists",
                "error": "Duplicate"
            }
        )
    )
    app.add_exception_handler(
        UserAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "User with email already exists",
                "error": "Email cannot be duplicate"
            }
        )
    )
    app.add_exception_handler(
        StudentAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "Student with Exam_id already exists",
                "error": "Exam_id cannot be duplicate"
            }
        )
    )
    app.add_exception_handler(
        AccessDenied,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "You do not have the permissions to perform this action",
                "error": "Access Denied"
            }
        )
    )
    app.add_exception_handler(
        AccessTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Provide a Valid Access Token",
                "error": "Access Token Required"
            }
        )
    )
    app.add_exception_handler(
        RefreshTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Provide a Valid Refresh Token",
                "error": "Refresh Token Required"
            }
        )
    )
    app.add_exception_handler(
        BookNotFound,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "Book is not found",
                "error": "Not Found"
            }
        )
    )
    app.add_exception_handler(
        TagNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Tag is not found",
                "error": "Not Found"
            }
        )
    )
    app.add_exception_handler(
        InvalidCredentials,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "Credentials Invalid or Incorrect",
                "error": "Request Error"
            }
        )
    )
    app.add_exception_handler(
        InvalidToken,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "Token is Invalid",
                "error": "Token Error"
            }
        )
    )
    app.add_exception_handler(
        RevokedToken,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "Token has been revoked, please Login in",
                "error": "Token Error"
            }
        )
    )
