from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse

from src.core.auth.session_user import get_current_user_from_session
from src.models.user import UserOrm
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
    user: UserOrm = Depends(get_current_user_from_session),
):
    logger.info(f"home {user=}")
    context = {
        "request": request,
        "user": user,
        "RO": False,
    }
    return templates.TemplateResponse(
        request,
        name="mailing/home.html",
        context=context,
    )

@router.get(
    "/{user_id}/home/",
    include_in_schema=False,
    name="home",
)
def home_by_id(
    user_id: str,
    request: Request,
    current_user: UserOrm = Depends(get_current_user_from_session),
):
    logger.info(f"home {current_user=}, {user_id=}")
    user = UserService.get_user_by_id(request, user_id)
    context = {
        "request": request,
        "user": user,
        "menu_username": current_user.username if user else "",
        "RO": True,
    }
    return templates.TemplateResponse(
        request,
        name="mailing/home.html",
        context=context,
    )

@router.get(
    "/verify-email/",
    include_in_schema=False,
    name="verify_email",
)
def verify_email(
    request: Request,
    user: UserOrm = Depends(get_current_user_from_session),
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
        err = UserService.patch_me(request, data)
        if error := err.setdefault("error", None):
            user = UserService.get_me(request)
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
