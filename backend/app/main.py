from fastapi import FastAPI
from app.routers import users, auth, chats, documents
from fastapi.middleware.cors import CORSMiddleware

app= FastAPI(title="DoodleTalkPro API")

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(chats.router)
app.include_router(documents.router)

@app.get("/")
async def root():
    return{"message":"API is LIVEEEEEEEEEEE!!!!!!!"}