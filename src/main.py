from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
import uvicorn


from src.api import router as api_router
from src.core.config import settings
from src.models.db_helper import db_helper

@asynccontextmanager
async def lifespan(app: FastAPI):
    await db_helper.init_db()
    # Startup
    yield
    # Shutdown
    await db_helper.dispose()


app = FastAPI(
    lifespan=lifespan,
    default_response_class=ORJSONResponse,
    title=settings.run.title,
    version=settings.run.version,
)


app.include_router(api_router, prefix=settings.api.prefix)


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
