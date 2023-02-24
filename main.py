import uvicorn
from fastapi import FastAPI
from src.routes import r_auth
from src.routes import r_genarticle
from src.controllers.c_genarticle import schedule_generate_and_post_article
from fastapi_utils.tasks import repeat_every


app = FastAPI()
app.include_router(r_auth.router)
app.include_router(r_genarticle.router)

@app.on_event("startup")
@repeat_every(seconds=60*(8*60))  # 8 hour
def  schedule_generate_and_post_task() -> None:
    schedule_generate_and_post_article()

if __name__=="__main__":
    print('[Server] Starting server')
    uvicorn.run("main:app",host='0.0.0.0', port=8080,  workers=1, reload=True)
