import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from src.utils.logger import error_logger
from src.api.core.config import settings
from src.api.core.socketio_server import socket_app
from src.api.v1.routers import main_router


app = FastAPI(
    title="TaskTaskGo API",
    description="API для управления задачами",
    version="1.0.0"
)

@app.middleware("http")
async def errors_to_telegram(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        error_logger.bind(method=request.method, path=str(request.url)).exception(f"Unhandled exception: {str(e)}")
        raise

app.include_router(main_router)

app.mount("/socket.io", socket_app, name="socketio")
app.mount("/static", StaticFiles(directory="static"), name="static")


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False,
    )