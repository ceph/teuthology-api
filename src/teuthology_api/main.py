import logging
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv

from teuthology_api.routes import suite, kill, login, logout, presets

load_dotenv()

DEPLOYMENT = os.getenv("DEPLOYMENT")
SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY")
PULPITO_URL = os.getenv("PULPITO_URL")
PADDLES_URL = os.getenv("PADDLES_URL")

log = logging.getLogger(__name__)
app = FastAPI()


@app.get("/")
def read_root(request: Request):
    """
    GET route for root.
    """
    return {"root": "success", "session": request.session.get("user", None)}


if DEPLOYMENT == "development":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[PULPITO_URL, PADDLES_URL],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET_KEY)
app.include_router(suite.router)
app.include_router(kill.router)
app.include_router(login.router)
app.include_router(logout.router)
app.include_router(presets.router)
