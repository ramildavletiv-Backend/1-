from uuid import uuid4

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from fastapi import HTTPException
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


class TaskUpdateSchema(BaseModel):
    title: str | None = None
    completed: bool | None = None


tasks: list[TaskSchema] = []
book: str = ""

@app.get("/tasks")
def read_tasks() -> list[TaskSchema]:
    return tasks

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
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


@app.patch("/tasks/{task_id}")
def update_task(task_id: str, payload: TaskUpdateSchema):
    for task in tasks:
        if task.id == task_id:
            if payload.title:
                task.title = payload.title
            if payload.completed is not None:
                task.completed = payload.completed
            return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id):
    for task in tasks:
        if task.id == task_id:
            tasks.remove(task)



class GetCategoriesSchema(BaseModel):
    id: str
    name: str

class PostCategoriesSchema(BaseModel):
    name: str

categories: list[GetCategoriesSchema] = []

@app.get("/categories",status_code=status.HTTP_200_OK)
def read_categories() -> list[GetCategoriesSchema]:
    return categories

@app.post("/categories", status_code=status.HTTP_201_CREATED)
def create_categories(payload: PostCategoriesSchema) -> GetCategoriesSchema:
    new_categories = GetCategoriesSchema(id=str (uuid4()), name=payload.name)
    categories.append(new_categories)
    return new_categories

@app.patch("/categories/{categories_id}", status_code=status.HTTP_200_OK)
def update_categories(categories_id: str, payload: PostCategoriesSchema) -> GetCategoriesSchema:
    for category in categories:
        if category.id == categories_id:
            if payload.name:
                category.name = payload.name
                return category
    raise HTTPException(status_code=404, detail="Category not found")

@app.delete("/categories/{categories_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_categories(categories_id: str):
    for category in categories:
        if category.id == categories_id:
            categories.remove(category)
            return
    raise HTTPException(status_code=404, detail="Category not found")