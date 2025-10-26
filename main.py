from fastapi import FastAPI

app = FastAPI()

@app.get('/status')
async def get_status():
    return({"status": "Server running"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0",reload=True, port=8000)
