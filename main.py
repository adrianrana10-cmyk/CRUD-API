from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from db import init_db, get_db

init_db()  # runs once at import time, before the app starts serving
app = FastAPI()

class TaskCreate(BaseModel):
    title: str = ""

@app.get("/")
def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/tasks", summary="List all tasks")
def get_tasks(db=Depends(get_db)):
    rows = db.execute("SELECT * FROM tasks").fetchall()
    result = []
    for row in rows:
        task = dict(row)
        task["done"] = bool(task["done"])
        result.append(task)
    return result

@app.get("/tasks/{task_id}", summary="Get a single task")
def get_task(task_id: int, db=Depends(get_db)):
    row = db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    task = dict(row)
    task["done"] = bool(task["done"])
    return task

@app.post("/tasks", status_code=201, summary="Create a task")
def create_task(task: TaskCreate, db=Depends(get_db)):
    if not task.title.strip():
        raise HTTPException(status_code=400, detail="title is required")
    cursor = db.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        (task.title, 0)
    )
    db.commit()
    new_id = cursor.lastrowid
    row = db.execute("SELECT * FROM tasks WHERE id = ?", (new_id,)).fetchone()
    result = dict(row)
    result["done"] = bool(result["done"])
    return result

class TaskUpdate(BaseModel):
    title: str = ""
    done: bool = False

@app.put("/tasks/{task_id}", summary="Update a task")
def update_task(task_id: int, update: TaskUpdate, db=Depends(get_db)):
    if not update.title.strip():
        raise HTTPException(status_code=400, detail="title is required")
    row = db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    db.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
        (update.title, int(update.done), task_id)
    )
    db.commit()
    updated = db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    result = dict(updated)
    result["done"] = bool(result["done"])
    return result

@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task")
def delete_task(task_id: int, db=Depends(get_db)):
    row = db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    db.commit()