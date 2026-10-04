from uuid import uuid4

from fastapi import FastAPI, status, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, DeclarativeBase, Mapped, sessionmaker, mapped_column
from contextlib import asynccontextmanager

DATABASE_URL = "postgresql+psycopg://postgres:admin@127.0.0.1:15432/postgres"
engine = create_engine(DATABASE_URL)
Sessionlocal = sessionmaker[Session](bind=engine)

class Base(DeclarativeBase):
    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid4()))

class TaskORM(Base):
    __tablename__ = "tasks"

    title: Mapped[str]
    completed: Mapped[bool] = mapped_column(default=False)

@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)

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

def get_db():
    db = Sessionlocal()

    try:
        yield db
    finally:
        db.close()

def task_orm_to_model(task_orm: TaskORM) -> TaskSchema:
    return TaskSchema(id=task_orm.id, title=task_orm.title, completed=task_orm.completed)

@app.get("/tasks")
def read_tasks(db: Session = Depends(get_db)) -> list[TaskSchema]:
    tasks_from_db = db.scalars(select(TaskORM)).all()
    return [task_orm_to_model(task) for task in tasks_from_db]

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_tasks(payload: TaskCreateSchema, db: Session = Depends(get_db)) -> TaskSchema:
    new_task = TaskORM(title=payload.title, completed=False)
    db.add(new_task)
    db.commit()

    return task_orm_to_model(new_task)


@app.patch("/tasks/{task_id}")
def update_task(task_id: str, payload: TaskUpdateSchema, db: Session = Depends(get_db)) -> TaskSchema:
    task_for_update = db.get(TaskORM, task_id)
    if payload.title:
        task_for_update.title = payload.title
    if payload.completed:
        task_for_update.completed = payload.completed

    db.commit()
    return task_for_update


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id, db: Session = Depends(get_db)) ->None:
    task_for_delete = db.get(TaskORM, task_id)
    db.delete(task_for_delete)
    db.commit()




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


