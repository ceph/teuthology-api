import logging
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from routes import suite, kill, login, logout
from dotenv import load_dotenv

load_dotenv()

DEPLOYMENT = os.getenv("DEPLOYMENT")
SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY")

log = logging.getLogger(__name__)
app = FastAPI(
    title="Teuthology API", description="REST API for executing Teuthology commands"
)


@app.get("/")
def read_root(request: Request):
    """
    GET route for root.
    """
    return {"root": "success", "session": request.session.get("user", None)}


if DEPLOYMENT == "development":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET_KEY)
app.include_router(suite.router)
app.include_router(kill.router)
app.include_router(login.router)
app.include_router(logout.router)
