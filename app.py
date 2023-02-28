import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from router import test, linebot

app = FastAPI(
    title="EduChatbot API",
    description="This API was developed for EduChatbot",
    version="1.0",
)

origins = [
    "*",
]

app.include_router(test.router)
app.include_router(linebot.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

if __name__ == "__main__":
    uvicorn.run("app:app",host="0.0.0.0", port=5000, reload=True)