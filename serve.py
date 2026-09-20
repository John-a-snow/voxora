import os
import sys
import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv


project_root = os.path.dirname(
    os.path.abspath(__file__)
)

sys.path.insert(
    0,
    project_root
)

load_dotenv(
    os.path.join(
        project_root,
        ".env"
    )
)

from app.api.routes import router


app = FastAPI(
    title="Voxora Voice RAG API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1|0\.0\.0\.0)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001
    )