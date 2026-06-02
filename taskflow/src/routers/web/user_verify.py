from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse

from src.services.user_service import UserService
from src.utils.jinja_templates import templates
from src.utils.loguru_config import AppLogger

logger = AppLogger().get_logger()
router = APIRouter(prefix="/user")


@router.get(
    "/home/",
    include_in_schema=False,
    name="home",
)
def home(
    request: Request,
):
    access_token = request.session.setdefault("access_token", None)
    if access_token:
        user = UserService.get_me(request, access_token)
        logger.info(f"home {user=}")
        context = {
            "request": request,
            "user": user,
        }
        return templates.TemplateResponse(
            request,
            name="mailing/home.html",
            context=context,
        )
    return RedirectResponse(url=request.url_for("login"), status_code=303)


@router.get(
    "/verify-email/",
    include_in_schema=False,
    name="verify_email",
)
def verify_email(
    request: Request,
):
    access_token = request.session.setdefault("access_token", None)
    if access_token:
        context = {
            "request": request,
            "token": access_token,
        }
        return templates.TemplateResponse(
            request,
            name="mailing/verification.html",
            context=context,
        )
    return RedirectResponse(url=request.url_for("login"), status_code=303)


@router.post(
    "/me/",
    include_in_schema=False,
    name="me",
)
def modify_me(
    request: Request,
    username: str = Form(None, description="username"),
    fullname: str = Form(None, description="fullname"),
    email: str = Form(None, description="email"),
    password: str = Form(None, description="password"),
):
    access_token = request.session.setdefault("access_token", None)
    if access_token:
        data = {
            "username": username,
            "fullname": fullname,
            "email": email,
            "password": password,
        }
        err = UserService.patch_me(request, access_token, data)
        if error := err.setdefault("error", None):
            user = UserService.get_me(request, access_token)
            context = {
                "error": error,
                "user": user,
            }
            return templates.TemplateResponse(
                request,
                name="mailing/home.html",
                context=context,
            )
    return RedirectResponse(url=request.url_for("home"), status_code=303)
