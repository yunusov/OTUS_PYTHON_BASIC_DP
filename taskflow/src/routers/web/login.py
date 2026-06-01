from typing import Annotated

from fastapi import APIRouter, Form, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse

from src.core import settings
from src.core.auth.fastapi_users import current_active_user
from src.models import UserOrm
from src.services.user_service import UserService
from src.utils.jinja_templates import templates
from src.utils.loguru_config import AppLogger
from src.utils.request_utils import async_request

logger = AppLogger().get_logger()
router = APIRouter()


@router.get("/", response_class=HTMLResponse, name="index")
def index(request: Request):
    access_token = request.session.setdefault("access_token", None)
    if access_token:
        user = UserService.get_me(request, access_token)
        if user:
            html_page = "index.html" if user.is_verified else "mailing/home.html"
            context = {
                "request": request,
                "user": user,
            }
            return templates.TemplateResponse(
                request,
                html_page,
                context,
            )
    return RedirectResponse(url=request.url_for("login"), status_code=303)


@router.get("/login/", response_class=HTMLResponse, name="login")
def login_get(request: Request):
    access_token = request.session.setdefault("access_token", None)
    if access_token:
        return RedirectResponse(url=request.url_for("index"), status_code=303)
    return templates.TemplateResponse(
        request,
        "login.html",
    )


@router.post("/login/", response_class=HTMLResponse)
def login_post(
    request: Request,
    user: Annotated[UserOrm | None, Depends(current_active_user)],
    username: str = Form(None, description="username"),
    password: str = Form(None, description="password"),
):
    logger.info(f"login post {user=}")
    if user is None:
        data = {
            "username": username,
            "password": password,
        }
        try:
            response = async_request(
                "POST",
                "/api/v1/auth/login",
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                request=request,
            )
            logger.info(f"login_post {response=}")
            if detail := response.setdefault("detail", None):
                if detail == "LOGIN_BAD_CREDENTIALS":
                    detail = "Неверный логин или пароль"
                return templates.TemplateResponse(
                    request,
                    "login.html",
                    {"error": detail},
                    status_code=400,
                )
            request.session["access_token"] = response["access_token"]
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return templates.TemplateResponse(
                request,
                "login.html",
                {"error": e},
                status_code=400,
            )
    return RedirectResponse(url=request.url_for("index"), status_code=303)


@router.get("/logout/", response_class=HTMLResponse)
def logout(
    request: Request,
):
    async_request(
        "POST",
        "/" + settings.api.v1.logout,
        request=request,
    )
    request.session.clear()
    return RedirectResponse(url=request.url_for("index"), status_code=303)
