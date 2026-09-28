from uuid import uuid4

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
)

class TaskSchema(BaseModel):
    id: str
    title: str
    completed: bool

class TaskCreateSchema(BaseModel):
    title: str

class BookSchema(BaseModel):
    book: str


tasks: list[TaskSchema] = []
book: str = ""

@app.get("/tasks")
def read_tasks() -> list[TaskSchema]:
    return tasks

@app.post("/tasks")
def create_tasks(payload: TaskCreateSchema) -> TaskSchema:
    new_task = TaskSchema(id=str (uuid4()), title=payload.title, completed=False)

    tasks.append(new_task)
    return new_task

@app.post("/book")
def create_book(payload: BookSchema) -> BookSchema:
    global book
    book = payload.book
    return payload

@app.get("/book")
def read_book() -> str:
    return f"Любимая книга: {book}"
