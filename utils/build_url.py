from config import SITE_URL


def change_password_url(refresh_password_token: str) -> str:
    return f"{SITE_URL}/refresh_password?token={refresh_password_token}"


def create_regional_agent_url() -> str:
    return f"{SITE_URL}/register/agent"
