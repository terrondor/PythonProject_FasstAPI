from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    # Определяем связь с постами
    posts = relationship("Post", back_populates="owner")

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)  # Добавление индекса для улучшения производительности поиска
    content = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Определяем связь с пользователем
    owner = relationship("User", back_populates="posts")