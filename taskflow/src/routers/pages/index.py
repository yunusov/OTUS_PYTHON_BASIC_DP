from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from src.template_config import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
        {"request": request},
    )
