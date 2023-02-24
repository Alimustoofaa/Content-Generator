import uvicorn
from fastapi import FastAPI
from src.routes import r_auth
from src.routes import r_genarticle


app = FastAPI()
app.include_router(r_auth.router)
app.include_router(r_genarticle.router)

if __name__=="__main__":
    print('[Server] Starting server')
    uvicorn.run("main:app",host='0.0.0.0', port=8080,  workers=1, reload=True)
