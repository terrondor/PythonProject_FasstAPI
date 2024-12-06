from pydantic import BaseModel

# Модель для создания пользователя
class UserCreate(BaseModel):
    username: str
    password: str
    confirm_password: str

# Модель для представления пользователя
class User(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True  # Позволяет использовать модель с SQLAlchemy

# Модель для создания поста
class PostCreate(BaseModel):
    title: str
    content: str

# Модель для представления поста
class Post(PostCreate):
    id: int
    owner_id: int

    class Config:
        orm_mode = True  # Позволяет использовать модель с SQLAlchemy