from deep_translator import GoogleTranslator
from typing import Annotated

from fastapi import APIRouter, Form, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse

from src.core import settings
from src.core.auth.session_user import get_current_user_from_session
from src.core.auth.fastapi_users import current_active_user
from src.models import UserOrm
from src.utils.jinja_templates import templates
from src.utils.loguru_config import AppLogger
from src.utils.request_utils import async_request

logger = AppLogger().get_logger()
router = APIRouter()
translator = GoogleTranslator(source='en', target='ru')


@router.get("/", response_class=HTMLResponse, name="index")
def index(request: Request,
          user: UserOrm = Depends(get_current_user_from_session),):
    logger.info(f"index {user=}")
    response = {}
    try:
        response = async_request(
            "GET",
            "https://api.adviceslip.com/advice",
            request=request,
        )
    except Exception as e:
        logger.error(f"index failed: {e}")

    eng_advice = response.setdefault("slip", {}).setdefault("advice", "")
    logger.info(f"index {eng_advice=}")
    random_tip = ""
    if eng_advice:
        random_tip = translator.translate(eng_advice, src='en', dest='ru')

    context = {
        "request": request,
        "user": user,
        "random_tip": random_tip if random_tip else "Начинай день с самых важных задач, двигайся только вперёд!",
    }
    html_page = "index.html" if user.is_verified else "mailing/home.html"
    return templates.TemplateResponse(
        request,
        html_page,
        context,
    )


@router.get("/login/", response_class=HTMLResponse, name="login")
def login_get(request: Request):
    logger.info("login_get")
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
    logger.info("logout")
    async_request(
        "POST",
        "/" + settings.api.v1.logout,
        request=request,
    )
    request.session.clear()
    return RedirectResponse(url=request.url_for("index"), status_code=303)
