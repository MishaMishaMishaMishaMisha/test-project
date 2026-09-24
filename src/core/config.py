from pydantic_settings import BaseSettings, SettingsConfigDict

from src.core.paths import ENV_FILE_PATH


class DBSettings(BaseSettings):
    
    HOST: str
    PORT: int
    DB: str # name
    USER: str
    PASSWORD: str
    
    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DB}"
    
    model_config = SettingsConfigDict(env_file=ENV_FILE_PATH,
                                      env_prefix="POSTGRES_",
                                      extra="ignore")


class RedisSettings(BaseSettings):
    
    HOST: str
    PORT: int
    PASSWORD: str
    
    model_config = SettingsConfigDict(env_file=ENV_FILE_PATH,
                                      env_prefix="REDIS_",
                                      extra="ignore")


class APPSettings(BaseSettings):
    
    HOST: str
    PORT: int
    
    model_config = SettingsConfigDict(env_file=ENV_FILE_PATH,
                                      env_prefix="APP_",
                                      extra="ignore")
    

class JWTSettings(BaseSettings):
    
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    
    model_config = SettingsConfigDict(env_file=ENV_FILE_PATH,
                                      env_prefix="JWT_",
                                      extra="ignore")


class ProjectSettings():
    
    db: DBSettings = DBSettings()
    redis: RedisSettings = RedisSettings()
    app: APPSettings = APPSettings()
    jwt: JWTSettings = JWTSettings()
    
    
settings = ProjectSettings()

        
        