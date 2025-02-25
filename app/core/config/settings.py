from dotenv import load_dotenv
from passlib.context import CryptContext
from pydantic import PostgresDsn, computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

from ..lib.databases import Databases, PostgreSQLDrivers

load_dotenv()


class DatabaseSettings(BaseSettings):
    """For default uses the Postgres"""

    ECHO_DEBUG_MODE: bool = False
    USED: Databases = Databases.PostgreSQL
    HOST: str
    PORT: int
    USER: str
    PASSWORD: str
    NAME: str

    model_config = SettingsConfigDict(env_prefix="DB_")

    @computed_field
    @property
    def postgres_url(self) -> PostgresDsn:
        """
        This is a computed field that generates a PostgresDsn URL

        The URL is built using the MultiHostUrl.build method, which takes the following parameters:
        - scheme: The scheme of the URL. In this case, it is "postgres".
        - username: The username for the Postgres database, retrieved from the POSTGRES_USER environment variable.
        - password: The password for the Postgres database, retrieved from the POSTGRES_PASSWORD environment variable.
        - host: The host of the Postgres database, retrieved from the POSTGRES_HOST environment variable.
        - path: The path of the Postgres database, retrieved from the POSTGRES_DB environment variable.

        Returns:
            PostgresDsn: The constructed PostgresDsn URL.
        """
        return MultiHostUrl.build(
            scheme=PostgreSQLDrivers.DEFAULT_DIALECT,
            username=self.USER,
            password=self.PASSWORD,
            host=self.HOST,
            path=self.NAME,
        )

    @computed_field
    @property
    def asyncpg_url(self) -> PostgresDsn:
        """
        This is a computed field that generates a PostgresDsn URL for asyncpg.

        The URL is built using the MultiHostUrl.build method, which takes the following parameters:
        - scheme: The scheme of the URL. In this case, it is "postgresql+asyncpg".
        - username: The username for the Postgres database, retrieved from the POSTGRES_USER environment variable.
        - password: The password for the Postgres database, retrieved from the POSTGRES_PASSWORD environment variable.
        - host: The host of the Postgres database, retrieved from the POSTGRES_HOST environment variable.
        - path: The path of the Postgres database, retrieved from the POSTGRES_DB environment variable.

        Returns:
            PostgresDsn: The constructed PostgresDsn URL for asyncpg.
        """
        return MultiHostUrl.build(
            scheme=f"{PostgreSQLDrivers.DEFAULT_DIALECT}+{PostgreSQLDrivers.DEFAULT_ASYNC_DRIVER}",
            username=self.USER,
            password=self.PASSWORD,
            host=self.HOST,
            path=self.NAME,
        )


class ApplicationSettings(BaseSettings):
    PRODUCTION: bool
    SITE_URL: str
    PWD_CONTEXT: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30 * 6
    REFRESH_PASSWORD_EXPIRE_MINUTES: int = 10
    VERIFICATION_CODE_EXPIRE_MINUTES: int = 10
    METRICS: bool


class MailSettings(BaseSettings):
    MAIN_ADDRESS: str
    MAIN_ADDRESS_PASSWORD: str
    HOST: str
    PORT: int
    TLS: bool
    model_config = SettingsConfigDict(env_prefix="MAIL_")


class Settings(BaseSettings):
    db: DatabaseSettings = DatabaseSettings()
    app: ApplicationSettings = ApplicationSettings()
    mail: MailSettings = MailSettings()


settings = Settings()
