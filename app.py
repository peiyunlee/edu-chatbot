import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from router import homework, linebot, task, student, reflect_task, reflect_hw, scheduler
from db import database



app = FastAPI(
    title="EduChatbot API",
    description="This API was developed for EduChatbot",
    version="1.0",
)

origins = [
    "*",
]

app.include_router(scheduler.router)
app.include_router(homework.router)
app.include_router(task.router)
app.include_router(student.router)
app.include_router(reflect_task.router)
app.include_router(reflect_hw.router)
app.include_router(linebot.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.on_event("shutdown")
def shutdown_db_client():
    database.client.close()

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)