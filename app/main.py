from fastapi import FastAPI
from pydantic import BaseModel

from app.routers import resumes

app = FastAPI()


@app.get("/")
def home():
    return {"message": "RecruitOS AI is running"}


class User(BaseModel):
    name: str
    email: str


@app.post("/users")
def create_user(user: User):
    return {
        "message": "User created successfully",
        "user": user
    }


app.include_router(resumes.router)