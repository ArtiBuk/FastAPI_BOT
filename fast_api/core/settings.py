from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    app_env: str = 'development'
    debug: bool = True
    db_user: str
    db_password: str
    db_address: str
    db_name: str
    root_path: str = ''
    secret_key: str
    salt: str

    class Config:
        env_file = '.env'

    @property
    def database_url(self) -> str:
        return "postgresql://" + self.db_user + ":" + \
            self.db_password + "@" + \
            self.db_address + "/" + self.db_name

    def is_production(self) -> bool:
        return self.app_env == 'production'

    def async_database_url(self):
        return self.database_url.replace('postgresql', 'postgresql+asyncpg', 1)
