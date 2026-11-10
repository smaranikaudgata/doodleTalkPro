from fastapi import FastAPI
from app.routers import users, auth, chats
app= FastAPI(title="DoodleTalkPro API")

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(chats.router)

@app.get("/")
async def root():
    return{"message":"API is LIVEEEEEEEEEEE!!!!!!!"}