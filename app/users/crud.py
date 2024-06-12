"""CRUD toolkit for users"""

from sqlalchemy.orm import Session

from app import fmodels
import app.database.models as models

def create_user(user: fmodels.SaltedUser, session: Session):
    """Creates a user given a username, salt, and password(hashed)"""
    if session:
        if not session.query(models.User).filter_by(username=user.username).first():
            user = models.User(username=user.username, password=user.password, salt=user.salt,
                                session="", session_exp=0)
            session.add(user)
            session.commit()
            session.refresh(user)
            return True
    return False


# Retrieves a user. Returns either a user or none in case of non-existent user.
def get_user_data(username: str, session: Session) -> models.User | None:
    if session:
        user = session.query(models.User).filter_by(username=username).first()
        if user:
            return user
    return None


# Function to update user.
# Returns False if failed, and True if success.
def update_user(username: str, new_settings: fmodels.UserRequestSetting, session: Session):
    if session:
        target_user = session.query(models.User).filter_by(username=username).first()

        if target_user:
            if new_settings.dictionary:
                target_user.dictionary = new_settings.dictionary
            
            if new_settings.theme is not None:
                target_user.theme = new_settings.theme

            session.commit()
            return True
    return False


def retrieve_users(session: Session):
    user_summary = []
    users = session.query(models.User).all()
    for user in users:
        user_detail = {}
        user_detail["name"] = user.username
        user_detail["id"] = user.id
        user_summary.append(user_detail)
    return user_summary