from app.core.config import settings


def change_password_url(refresh_password_token: str) -> str:
    return f"{settings.app.SITE_URL}/refresh_password?token={refresh_password_token}"
