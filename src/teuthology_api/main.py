import logging
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from teuthology_api.config import settings
from teuthology_api.routes import suite, kill, login, logout, presets


DEPLOYMENT = settings.deployment
SESSION_SECRET_KEY = settings.session_secret_key
PULPITO_URL = settings.pulpito_url
PADDLES_URL = settings.paddles_url

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
