from fastapi import FastAPI

from mancala.app.core.middleware import configure_middleware
from mancala.app.api.router import game


app = FastAPI(
    title="Mancala Game API",
    description="A REST API for playing the Mancala game",
    version="0.1.0",
)
app.include_router(game.router, prefix="/api/v1/games", tags=["games"])

configure_middleware(app)


@app.get("/")
async def root():
    return {"message": "Welcome to the Mancala Game API!", "docs": "/docs"}
