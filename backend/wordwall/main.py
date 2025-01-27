################################################################################
"""
WordWall - Simple, Self-Hosted, Collaborative Word Cloud Generator.

(c) 2025 | Stanley Solutions | Joe Stanley
License: MIT
"""
################################################################################
# pylint: disable=no-member

from typing import Annotated
from tempfile import TemporaryDirectory
from pathlib import Path
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request, Cookie
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from loguru import logger

from . import __header__, __version__, api
from .configuration import settings
from .database import connect_database
from .session import Manager


__html_header__ = __header__.replace("\n", r"\n")

APP_COOKIE_NAME: str = "client_token"

main_manager = Manager()

@asynccontextmanager
async def lifespan(_: FastAPI):
    """Application Lifespan System."""
    # Setup
    logger.info(__header__)
    logger.info(f"Version: {__version__}")
    # Manage Temporary Database File Contextually
    with TemporaryDirectory() as tmp_directory:
        db_file = Path(tmp_directory) / "words.db"
        logger.debug(f"Temporary Database File: {db_file}")
        await connect_database(database_path=db_file)
        yield

app = FastAPI(
    title="WordWall",
    summary="Simple, Self-Hosted, Collaborative Word Cloud Generator.",
    version=__version__,
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:8000", # Uvicorn Default Server
    ] + settings.application.cross_site_origins,
    # pylint: enable=no-member
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api.router)

# Mount the Static File Path
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent/"static"),
    name="static"
)

# Load Templates
TEMPLATES: Jinja2Templates = Jinja2Templates(
    directory=(Path(__file__).parent/"templates"),
)

################################################################################

def ensure_base_url(request: Request):
    """Ensure the Base URL is Set."""
    if settings.application.site_url in ["", None]:
        settings.application.site_url = (
            f"{request.base_url.scheme}://{request.base_url.netloc}"
        )
        settings.update()

def core_response(
    request: Request,
    wall_id: str | None,
    wall_hash: str | None
) -> HTMLResponse:
    """Core Response Builder."""
    ensure_base_url(request=request)
    return TEMPLATES.TemplateResponse(
        "index.html",
        {
            "request": request,
            "console_app_name": __html_header__,
            "wall_id": wall_id,
            "wall_hash": wall_hash,
            "site_name": settings.application.site_name,
            "defer_url": settings.application.site_url,
        },
    )

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root(request: Request) -> HTMLResponse:
    """Main Application Landing - Allow Creation of New Wall and Token."""
    wall = main_manager.new_wall()
    return core_response(request=request, wall_id=wall.id, wall_hash=wall.hash)

@app.get("/host/{wall_id}", response_class=HTMLResponse, include_in_schema=False)
async def operate_wall(request: Request, wall_id: str) -> HTMLResponse:
    """Generate the New Data Store for a New Wall - Operate as Moderator."""
    try:
        return core_response(
            request=request,
            wall_id=wall_id,
            wall_hash=main_manager.get_by_id(wall_id).hash,
        )
    except AttributeError:
        return RedirectResponse(
            url=f"{settings.application.site_url}?wall_not_found",
        )

@app.get("/play/{wall_hash}", response_class=HTMLResponse, include_in_schema=False)
@app.get("/review/{wall_hash}", response_class=HTMLResponse, include_in_schema=False)
async def participant_page(
    request: Request,
    # Hash of the Wall ID
    wall_hash: str,
    # Unique ID for Participant
    client_token: Annotated[str | None, Cookie()] = None,
) -> HTMLResponse:
    """Participant's Interaction Point - Use Wall."""
    if main_manager.get_by_hash(wall_hash) is None:
        ensure_base_url(request=request)
        return RedirectResponse(
            url=f"{settings.application.site_url}?wall_not_found",
        )
    if not client_token:
        client_token = str(uuid4())
    response = core_response(
        request=request,
        wall_id=main_manager.get_by_hash(wall_hash).id,
        wall_hash=wall_hash,
    )
    response.set_cookie(APP_COOKIE_NAME, client_token)
    return response
