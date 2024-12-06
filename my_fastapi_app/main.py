from fastapi import FastAPI, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import models
import schemas
import database
import auth


app = FastAPI()
templates = Jinja2Templates(directory="templates")

database.Base.metadata.create_all(bind=database.engine)


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username==username).first()
    if not user or not auth.verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
def register(
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    print("Регистрация пользователя:", username)

    existing_user = db.query(models.User).filter(models.User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    if password != confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    hashed_password = auth.hash_password(password)
    db_user = models.User(username=username, hashed_password=hashed_password)

    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        print(e)  # Для отладки
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")

    print("Пользователь успешно зарегистрирован:", db_user.username)

    # После успешной регистрации перенаправляем пользователя на страницу входа
    return RedirectResponse(url='/login', status_code=status.HTTP_302_FOUND)


@app.get("/posts", response_class=HTMLResponse)
async def read_posts(request: Request, db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return templates.TemplateResponse("posts.html", {"request": request, "posts": posts})


@app.get("/posts/{post_id}", response_class=HTMLResponse)
async def read_post(post_id: int, request: Request, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id==post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return templates.TemplateResponse("post_detail.html", {"request": request, "post": post})


@app.post("/posts")
async def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    db_post = models.Post(**post.dict(), owner_id=1)  # Здесь нужно указать ID текущего пользователя
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return RedirectResponse(url='/posts', status_code=status.HTTP_302_FOUND)
