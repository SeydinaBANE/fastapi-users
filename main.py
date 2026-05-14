"""Point d'entrée : composition root, configure logging, monte le routeur."""

import logging

from fastapi import FastAPI

from api.router import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

app = FastAPI(title="FastAPI Users", version="1.0.0")
app.include_router(router)
