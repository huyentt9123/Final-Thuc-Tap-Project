from pydantic import BaseModel

class Settings(BaseModel):
    MONGODB_URL: str = "mongodb+srv://huyentt:1234567890@cluster0.hhai9br.mongodb.net/recommend_system"
    DATABASE_NAME: str = "recommend_system"
    class Config:
        env_file = ".env"
settings = Settings()
