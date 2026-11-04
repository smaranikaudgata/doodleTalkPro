from fastapi import FastAPI
app= FastAPI(title="DoodleTalkPro API")

@app.get("/")
async def root():
    return{"message":"API is LIVEEEEEEEEEEE!!!!!!!"}