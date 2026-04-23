# from fastapi import FastAPI
# from pydantic import BaseModel
#
# app = FastAPI()
#
# users = []
#
# class User(BaseModel):
#     id : int
#     name :str
#     age : int
#
# #create user
# @app.post("/users")
# def create_user(user:User):
#     users.append(user)
#     return {"message":"user created","user":user}
#
# #get all users
# @app.get("/users")
# def get_allusers():
#     return users
#
# #get sigle user
# @app.get("/users/{user_id}")
# def get_user(user_id:int):
#     for user in users:
#         if user.id == user_id:
#             return user
#     return {"error":"user not found"}
#
# @app.put("/users/{user_id}")
# def update_user(user_id: int, updated_user: User):
#     for i, user in enumerate(users):
#         if user.id == user_id:
#             users[i] = updated_user
#             return {"message": "User updated", "user": updated_user}
#     return {"error": "User not found"}
#
# # Delete user
# @app.delete("/users/{user_id}")
# def delete_user(user_id: int):
#     for i, user in enumerate(users):
#         if user.id == user_id:
#             users.pop(i)
#             return {"message": "User deleted"}
#     return {"error": "User not found"}
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import models
from database import SessionLocal, engine
from pydantic import BaseModel

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Pydantic schema (for request)
class UserCreate(BaseModel):
    name: str
    age: int

# Dependency to get DB session
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create user
@app.post("/users")
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = models.User(name=user.name, age=user.age)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Get all users
@app.get("/users")
async def get_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()

# Get single user
@app.get("/users/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    return db.query(models.User).filter(models.User.id == user_id).first()

#updaet user
@app.put("/users/{user_id}")
async def update_user(user_id: int, updated_user: UserCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if user:
        user.name = updated_user.name
        user.age = updated_user.age
        db.commit()
        db.refresh(user)
        return user

    return {"error": "User not found"}

# Delete user
@app.delete("/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        return {"message": "User deleted"}
    return {"error": "User not found"}