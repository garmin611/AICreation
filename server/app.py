import signal
import sys
import os

from fastapi.responses import JSONResponse



sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from server.config.config import load_config
from server.controllers.project_controller import router as project_router
from server.controllers.chapter_controller import router as chapter_router
from server.controllers.media_controller import router as media_router
from server.controllers.admin_controller import router as admin_router
from server.controllers.entity_controller import router as entity_router
from server.controllers.video_controller import router as video_router
from server.utils.response import make_response

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


# 全局异常处理器 但是似乎不能很好的使用
@app.exception_handler(Exception)
async def handle_error(request, exc):
 
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.detail},
            media_type="application/json",
        )
    
    return JSONResponse(
        status_code=200,
        content=make_response(status='error', msg=str(exc)),
        media_type="application/json",
    )

# Register routers
app.include_router(project_router)
app.include_router(chapter_router)
app.include_router(media_router)
app.include_router(admin_router)
app.include_router(entity_router)
app.include_router(video_router)

def signal_handler(signal, frame):
    sys.exit(0)



if __name__ == '__main__':
    import uvicorn
    config = load_config()
    signal.signal(signal.SIGINT, signal_handler)
    uvicorn.run("server.app:app", host=config.get('server', {}).get('host', '0.0.0.0'),
                port=config.get('server', {}).get('port', 5001),
                reload=True)
