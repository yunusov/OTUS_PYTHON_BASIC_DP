from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from src.template_config import templates

router = APIRouter(prefix="/auth", tags=["Auth pages"])


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        request,
        "login.html",
        {"request": request},
    )
