import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.config.config import load_config
from server.controllers.project_controller import router as project_router
from server.controllers.chapter_controller import router as chapter_router
from server.controllers.media_controller import router as media_router
from server.controllers.admin_controller import router as admin_router
from server.controllers.character_controller import router as character_router
from server.controllers.video_controller import router as video_router

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)



# Register routers
app.include_router(project_router)
app.include_router(chapter_router)
app.include_router(media_router)
app.include_router(admin_router)
app.include_router(character_router)
app.include_router(video_router)

@app.exception_handler(Exception)
async def handle_error(request, exc):
    return {"error": str(exc), "status": "error"}

if __name__ == '__main__':
    import uvicorn
    config = load_config()
    uvicorn.run("server.app:app", host=config.get('server', {}).get('host', '0.0.0.0'),
                port=config.get('server', {}).get('port', 5000),
                reload=True)
