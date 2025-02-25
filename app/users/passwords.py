from app.core.config import settings


def verify_password(plain_password, hashed_password):
    return settings.app.PWD_CONTEXT.verify(plain_password, hashed_password)


def get_password_hash(password):
    return settings.app.PWD_CONTEXT.hash(password)
