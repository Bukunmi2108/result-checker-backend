from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import Body, HTTPException, status, BackgroundTasks
import logging
from .schemas import RevokedTokenModel, UserCreateModel, StudentCreateModel, ExamCentreCreateModel, AdminCreateModel, SubjectCreateModel
from .models import RevokedToken, Student, User, ExamCentre, Admin, Subject
from sqlmodel import select, desc
from .utils import generate_passwd_hash, create_safe_url
from .errors import (UserAlreadyExists, AdminAlreadyExists, UserNotFound, ExamIdNotFound, CenterNoNotFound, StudentAlreadyExists, StudentNotFound, CentreAlreadyExists, CentreNotFound, SubjectNotFound, SubjectAlreadyExists)
from .config import settings
from .mail import create_message, mail
import uuid


class TokenService:
    async def add_token_to_blacklist(self, session:AsyncSession, token_jti: RevokedTokenModel):
        try:
            new_revoked_token = RevokedToken(
                token_jti= token_jti
            )

            session.add(new_revoked_token)
            await session.commit()

            return new_revoked_token
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error is {e}")

    async def get_token_from_blacklist(self, session:AsyncSession, token_jti: RevokedTokenModel) -> bool:
        try:
            statement = select(RevokedToken).where(RevokedToken.token_jti == token_jti)

            result = await session.exec(statement)
            return True if result.first() else None
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error is {e}")

class UserService:
    async def get_student_by_exam_id(self, exam_id: str, session: AsyncSession):
        
        student = select(Student).where(Student.exam_id == exam_id)

        result = await session.exec(student)
        return result.first() if result else None
    
    async def get_student_by_exam_centre_no(self, exam_centre_no: str, session: AsyncSession):
        
        student = select(Student).where(Student.exam_centre_no == exam_centre_no)

        result = await session.exec(student)
        return result.first() if result else None
    
    async def get_user_by_uid(self, uid: str, session: AsyncSession):
        user = select(User).where(User.uid == uid)

        result = await session.exec(user)
        return result.first() if result else None

    async def get_user_by_email(self, email: str, session: AsyncSession):
        user = select(User).where(User.email == email)

        result = await session.exec(user)
        return result.first() if True else None
        
    
    async def get_all_users(self, session: AsyncSession):
        statement = select(User).order_by(desc(User.created_at))

        result = await session.exec(statement)
        return result.all() if result else None
        
    async def confirm_payments(self, user_uid: str, session: AsyncSession):
        user = await self.get_user_by_uid(user_uid, session)
        if user:
            user.is_paid = True
            await session.commit()
            return user
        raise UserNotFound()
    
    async def request_approval(self, user_uid: str, exam_id: str, session: AsyncSession):
        student = await StudentService().get_a_student_by_exam_id(exam_id, session)
        if not student:
            raise StudentNotFound()
        
        user = await self.get_user_by_uid(user_uid, session)
        if not user:
            raise UserNotFound()
        
        if user.is_paid and not student.is_approved:
            student.is_approved = True
            await session.commit()
            return student

        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User has not paid")
    
    async def create_a_user(self, user_data: UserCreateModel, background_tasks: BackgroundTasks, session: AsyncSession):
        user_data_dict = user_data.model_dump()

        email = user_data_dict["email"]

        if await self.get_user_by_email(email, session):
            raise UserAlreadyExists()
        
        new_user = User(
            **user_data_dict
        )
        new_user.password = generate_passwd_hash(new_user.password)

        #######################
        safe_url = create_safe_url( str(new_user.uid), new_user.email)

        html = f"""<>
                    <h1>Welcome to the App</h1></br>
                    <p>Congratulations, you have successfully signed up</p></br>
                    <p>Click <a href="{settings.DOMAIN_URL}/api/v1/user/verify_safe_url/{safe_url}">here</a> to verify your account</p>
                    </>
                """
        message = create_message(
            recipients=[new_user.email],
            subject='Activation Link',
            body=html
        )

        background_tasks.add_task(mail.send_message, message)
        ############################

        session.add(new_user)
        await session.commit()
        return new_user

       
    async def update_a_user(self, user_uid: str, user_data: dict, session: AsyncSession):
        try:
            exam_id = user_data.get('exam_id')
            exam_centre_no = user_data.get('exam_centre_no')

            if exam_id:
                exam_id_check = await StudentService().get_a_student_by_exam_id(exam_id, session)
                if exam_id_check is None:
                    raise ExamIdNotFound()

            if exam_centre_no:
                exam_centre_no_check = await ExamCentreService().get_exam_centre_by_exam_centre_no(exam_centre_no, session)
                if exam_centre_no_check is None:
                    raise CenterNoNotFound()

            user_to_update = await self.get_user_by_uid(uid=user_uid, session=session)
            if user_to_update:
                for k, v in user_data.items():
                    setattr(user_to_update, k, v)
                await session.commit()
                return user_to_update
            else:
                raise UserNotFound()
        except (ExamIdNotFound, CenterNoNotFound, UserNotFound) as e: 
            raise e  # Re-raise the exception
        except Exception as e:
            raise e
    
    async def delete_a_user(self, user_uid: str, session: AsyncSession):
        user_to_delete = await self.get_user_by_uid(user_uid, session)

        if user_to_delete is not None:
            await session.delete(user_to_delete)
            await session.commit()
        else:
            raise UserNotFound()
    
class StudentService:
    async def get_a_student(self, uid: str, session: AsyncSession):
        statement = select(Student).where(Student.uid == uid)

        result = await session.exec(statement)

        if result is None:
            raise StudentNotFound()
        
        return result.first() 

    async def get_a_student_by_exam_id(self, exam_id: str, session: AsyncSession):
        statement = select(Student).where(Student.exam_id == exam_id)

        result = await session.exec(statement)

        if result is None:
            raise StudentNotFound()
        return result.first() 
        
    async def get_all_students(self, session: AsyncSession):
            statement = select(Student).order_by(desc(Student.created_at))

            result = await session.exec(statement)

            if result is None:
                raise StudentNotFound()
            return result.all() 
        
    async def create_a_student(self, session: AsyncSession, student_data: StudentCreateModel = Body(...)):
        student_data_dict = student_data.model_dump()

        random_code = str(uuid.uuid4())[:8]
        student_data_dict["exam_id"] = random_code

        exam_id_check = await UserService().get_student_by_exam_id(student_data_dict["exam_id"], session) 
        
        centre_no_check = await ExamCentreService().get_exam_centre_by_exam_centre_no(student_data_dict["exam_centre_no"], session)

        if centre_no_check is not None:            
            if exam_id_check is None:
                new_student = Student(
                    **student_data_dict
                )
                session.add(new_student)
                await session.commit()

                return new_student
            
            raise StudentAlreadyExists()
        raise CenterNoNotFound()

    async def update_a_student(self, student_uid: str, student_data: dict, session: AsyncSession):
        student_to_update = await self.get_a_student(student_uid, session)

        if student_to_update:
            for k, v in student_data.items():
                setattr(student_to_update, k, v)

            await session.commit()

            return student_to_update
        
        raise StudentNotFound()

    async def update_student_results(self, exam_centre_no: str, subject_code: str, result_data: dict, session: AsyncSession):
        """
        Updates the results of students for a given subject and exam center.

        Args:
            exam_centre_no (str): The exam center number.
            subject_code (str): The subject code.
            result_data (dict): A dictionary containing exam IDs as keys and grades as values.
            session (AsyncSession): An asynchronous database session.
            
        Returns:
            str: "done" if the operation is successful.
        """
            
        subject = await SubjectService().get_subject_by_code(subject_code, session)
        subject_name = subject.subject_name

        exam_centre_check = await ExamCentreService().get_exam_centre_by_exam_centre_no(exam_centre_no, session)
        if exam_centre_check is None:
            raise CentreNotFound()
        
        for exam_id, grade in result_data.items():
            student = await StudentService().get_a_student_by_exam_id(exam_id, session)
            if student:
                existing_result = student.result

                new_result = {
                    **existing_result,
                    subject_name: grade
                }

                setattr(student, "result", new_result)
                await session.commit()

            else:
                raise StudentNotFound()
        
        return "done"

    async def delete_a_student(self, student_uid: str, session: AsyncSession):
        student_to_delete = await self.get_a_student(student_uid, session)
        
        if student_to_delete is None:
            raise StudentNotFound()
        
        await session.delete(student_to_delete)
        await session.commit()
      
class ExamCentreService:
    async def get_exam_centre_by_exam_centre_no(self, exam_centre_no: str, session: AsyncSession):
        statement = select(ExamCentre).where(ExamCentre.exam_centre_no == exam_centre_no)
        result = await session.exec(statement)

        if result is None:
            raise CentreNotFound()
        return result.first() 

    async def get_all_exam_centres(self, session: AsyncSession):
        statement = select(ExamCentre).order_by(desc(ExamCentre.created_at))
        result = await session.exec(statement)

        if result is None:
            raise CentreNotFound()
        
        return result.all()
 
    async def get_exam_centre_by_exam_centre_uid(self, exam_centre_uid: str, session: AsyncSession):
        statement = select(ExamCentre).where(ExamCentre.uid == exam_centre_uid)
        result = await session.exec(statement)

        if result is None:
            print("123")
            raise CentreNotFound()
        
        return result.first()

    async def create_an_exam_centre(self, exam_centre_data: ExamCentreCreateModel, session: AsyncSession):
        exam_centre_data_dict = exam_centre_data.model_dump()

        random_code = str(uuid.uuid4())[:6]
        exam_centre_data_dict["exam_centre_no"] = random_code

        exam_centre_no = exam_centre_data_dict["exam_centre_no"]

        if await self.get_exam_centre_by_exam_centre_no(exam_centre_no, session):
            raise CentreAlreadyExists()
        
        new_centre = ExamCentre(**exam_centre_data_dict)

        session.add(new_centre)
        await session.commit()

        return new_centre

    async def update_an_exam_centre(self, exam_centre_uid: str, exam_centre_data: dict, session: AsyncSession):
        exam_centre_to_update = await self.get_exam_centre_by_exam_centre_uid(exam_centre_uid, session)
        if exam_centre_to_update:
            for k, v in exam_centre_data.items():
                setattr(exam_centre_to_update, k, v)
            await session.commit()
            return exam_centre_to_update
        raise CentreNotFound()

    async def delete_an_exam_centre(self, exam_centre_uid: str, session: AsyncSession):
        exam_centre_to_delete = await self.get_exam_centre_by_exam_centre_uid(exam_centre_uid, session)
        if exam_centre_to_delete:
            await session.delete(exam_centre_to_delete)
            await session.commit()
        else:
            raise CentreNotFound()
        
class AdminService:
    async def get_admin_by_email(self, email: str, session: AsyncSession):
        try:
            statement = select(Admin).where(Admin.email == email)
            result = await session.exec(statement)
            return result.first() if result else None
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error is {e}")

    async def get_super_user_by_email(self, session: AsyncSession):
        try:
            statement = select(Admin).where(Admin.email == settings.SUPER_ADMIN_EMAIL)
            result = await session.exec(statement)
            return result.first() if result else None
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error is {e}")

    async def get_admin_by_uid(self, uid: str, session: AsyncSession):
        try:
            statement = select(Admin).where(Admin.uid == uid)
            result = await session.exec(statement)
            return result.first() if result else None
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error is {e}")

    async def get_all_admins(self, session: AsyncSession):
        statement = select(Admin).order_by(desc(Admin.created_at))
        result = await session.exec(statement)
        return result.all() if result else None

    async def create_super_admin(self, background_tasks: BackgroundTasks, session: AsyncSession):
        admin_data = {
            "email": settings.SUPER_ADMIN_EMAIL,
            "password": generate_passwd_hash(settings.SUPER_ADMIN_PASSWORD),
            "first_name": settings.SUPER_ADMIN_FIRSTNAME,
            "last_name": settings.SUPER_ADMIN_LASTNAME,
            "phone_number": settings.SUPER_ADMIN_PHONE_NUMBER,
        }

        html = f"""<body>
                    <h1>Welcome to Resultify</h1></br>
                    <p>First Name: {settings.SUPER_ADMIN_FIRSTNAME}</p>
                    <p>Last Name: {settings.SUPER_ADMIN_LASTNAME}</p>
                    <p>Email: {settings.SUPER_ADMIN_EMAIL}</p>
                    <p>Password: {settings.SUPER_ADMIN_PASSWORD}</p>
                </body>"""

        message = create_message(
            recipients=[settings.SUPER_ADMIN_EMAIL],
            subject='Resultify Super Admin Details',
            body=html
        )

        email_check = await self.get_super_user_by_email(session)

        if email_check is None:
            new_admin = Admin(**admin_data)
            new_admin.role = "super_admin"

            background_tasks.add_task(mail.send_message, message)
            
            session.add(new_admin)
            await session.commit()

            return new_admin
        raise AdminAlreadyExists()

    async def create_an_admin(self, background_tasks: BackgroundTasks, admin_data: AdminCreateModel, session: AsyncSession):
        admin_data_dict = admin_data.model_dump()
        email = admin_data_dict["email"]

        if await self.get_admin_by_email(email, session):
            raise AdminAlreadyExists()
        
        random_code = str(uuid.uuid4())[:12]
        admin_data_dict["password"] = random_code

        new_admin = Admin(**admin_data_dict)
        new_admin.password = generate_passwd_hash(new_admin.password)

        html = f"""<body>
            <h1>Welcome to Resultify</h1></br>
            <p>Here is your Admin Login Info</p>
            <p>Email: {new_admin.email}</p>
            <p>Password: {new_admin.password}</p>
        </body>"""

        message = create_message(
            recipients=[new_admin.email],
            subject='Resultify Admin Details',
            body=html
        )

        background_tasks.add_task(mail.send_message, message)

        session.add(new_admin)
        await session.commit()

        return new_admin

    async def update_an_admin(self, admin_uid: str, admin_data: dict, session: AsyncSession):
        try:
            admin_to_update = await self.get_admin_by_uid(admin_uid, session)
            if admin_to_update:
                for k, v in admin_data.items():
                    setattr(admin_to_update, k, v)
                await session.commit()
                return admin_to_update
            raise UserNotFound()
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error is {e}")

    async def delete_an_admin(self, admin_uid: str, session: AsyncSession):
        try:
            admin_to_delete = await self.get_admin_by_uid(admin_uid, session)
            if admin_to_delete:
                await session.delete(admin_to_delete)
                await session.commit()
            else:
                raise UserNotFound()
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error is {e}")

class SubjectService:
    async def get_all_subjects(self, session: AsyncSession):
        statement = select(Subject).order_by(Subject.subject_name)
        result = await session.exec(statement)
        return result.all() if result else None
    
    async def get_subject_by_uid(self, uid: str, session: AsyncSession):
        statement = select(Subject).where(Subject.uid == uid)
        result = await session.exec(statement)

        if result is None:
            raise SubjectNotFound()
        return result.first()
    
    async def get_subject_by_code(self, code: str, session: AsyncSession):
        statement = select(Subject).where(Subject.subject_code == code)
        result = await session.exec(statement)

        if result is None:
            raise SubjectNotFound()
        return result.first()
    
    async def get_subject_by_name(self, name: str, session: AsyncSession):
        statement = select(Subject).where(Subject.subject_name == name)
        result = await session.exec(statement)

        if result is None:
            raise SubjectNotFound()
        return result.first()
    
    async def create_a_subject(self, subject_data: SubjectCreateModel, session: AsyncSession):
        subject_data_dict = subject_data.model_dump()

        random_code = str(uuid.uuid4())[:6]
        subject_data_dict["subject_code"] = random_code

        subject_code = subject_data_dict["subject_code"]
        subject_name = subject_data_dict["subject_name"]

        if not subject_name:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Subject name is required")

        if await self.get_subject_by_code(subject_code, session):
            raise SubjectAlreadyExists()
        
        if await self.get_subject_by_name(subject_name, session):
            raise SubjectAlreadyExists()
        
        new_subject = Subject(**subject_data_dict)

        session.add(new_subject)
        await session.commit()

        return new_subject
    
    async def update_a_subject(self, subject_uid: str, subject_data: SubjectCreateModel, session: AsyncSession):
        subject_to_update = await self.get_subject_by_uid(subject_uid, session)
        if subject_to_update:
            for k, v in subject_data.items():
                setattr(subject_to_update, k, v)
            await session.commit()
            return subject_to_update
        raise SubjectNotFound()
    
    async def delete_a_subject(self, subject_uid: str, session: AsyncSession):
        subject_to_delete = await self.get_subject_by_uid(subject_uid, session)
        if subject_to_delete:
            await session.delete(subject_to_delete)
            await session.commit()
        else:
            raise SubjectNotFound()