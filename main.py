from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
import models
import schemas
from security import hash_password, verify_password, create_access_token

app = FastAPI(title="מערכת ניהול משימות")


# תלות: פותחת סשן לכל בקשה וסוגרת בסיומה
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------- Authentication / Register ----------
@app.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # 1. בדיקה האם המשתמש כבר קיים לפי שם המשתמש או האימייל
    existing_user = db.query(models.User).filter(models.User.name == user.name).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="שם המשתמש כבר תפוס")

    # 2. ביצוע Hash לסיסמה לפני שמירה
    hashed_pwd = hash_password(user.password)

    # 3. יצירת אובייקט המשתמש ושמירת ה-Hash בשדה המתאים במסד הנתונים
    new_user = models.User(
        name=user.name,  # שם המשתמש נשמר בשדה name ב-DB
        email=user.email,  # אימייל (אם קיים בסכמה שלך)
        hashed_password=hashed_pwd  # שמירת הסיסמה המוצפנת בלבד!
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 4. החזרת האובייקט - FastAPI ימיר אותו אוטומטית לפי סכמת UserResponse (id ו-username בלבד)
    return new_user

# ---------- Authentication / Login ----------
@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # 1. חיפוש המשתמש במסד הנתונים לפי שם המשתמש שהוזן בטופס
    user = db.query(models.User).filter(models.User.name == form_data.username).first()

    # 2. בדיקה שהמשתמש קיים ושהסיסמה תואמת ל-Hash השמור ב-DB
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="שם משתמש או סיסמה שגויים",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. הנפקת טוקן JWT עם מזהה המשתמש
    access_token = create_access_token(data={"sub": str(user.id)})

    # 4. החזרת הטוקן למבקש
    return {"access_token": access_token, "token_type": "bearer"}
# ---------- Users (הנתיבים הקיימים שלך) ----------
@app.get("/users", response_model=list[schemas.UserOut])
def get_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()


@app.get("/users/{user_id}", response_model=schemas.UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="המשתמש לא נמצא")
    return user


@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="המשתמש לא נמצא")
    db.delete(user)
    db.commit()
    return {"message": "המשתמש נמחק"}