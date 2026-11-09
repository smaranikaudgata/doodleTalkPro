from fastapi import FastAPI
from routers import users, auth
app= FastAPI(title="DoodleTalkPro API")

app.include_router(users.router)
app.include_router(auth.router)

@app.get("/")
async def root():
    return{"message":"API is LIVEEEEEEEEEEE!!!!!!!"}