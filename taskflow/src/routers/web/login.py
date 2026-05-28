from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from src.models.user import UserOrm
from src.core.database import get_db_helper
from passlib.context import CryptContext
from sqlalchemy import select

router = APIRouter(prefix="/auth", tags=["Auth pages"])


async def get_current_user(request: Request):
    return request.session.get("user")


@router.get("/login")
async def login_page(request: Request, user=Depends(get_current_user)):
    if user:
        return RedirectResponse(url="/", status_code=302)

    from src.utils.jinja_templates import templates

    html = templates.get_template("login.html").render(
        request=request, user=None, error=None
    )
    return HTMLResponse(html)


@router.post("/login")
async def login_web(
    request: Request, username: str = Form(...), password: str = Form(...)
):

    # argon2 (как в fastapi-users)
    pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

    try:
        db_helper = get_db_helper()
        db = await anext(db_helper.get_session())

        # Ищем пользователя по email
        result = await db.execute(select(UserOrm).where(UserOrm.email == username))
        user = result.scalar_one_or_none()

        if not user:
            # Пробуем по username
            result = await db.execute(
                select(UserOrm).where(UserOrm.username == username)
            )
            user = result.scalar_one_or_none()

        if not user:
            from src.utils.jinja_templates import templates

            html = templates.get_template("login.html").render(
                request=request, user=None, error="Неверный email или пароль"
            )
            return HTMLResponse(html)

        # Проверяем пароль через argon2
        if not pwd_context.verify(password, user.hashed_password):
            from src.utils.jinja_templates import templates

            html = templates.get_template("login.html").render(
                request=request, user=None, error="Неверный email или пароль"
            )
            return HTMLResponse(html)

        # Пароль верный — сохраняем в session
        request.session["user"] = {
            "email": user.email,
            "id": str(user.id),
        }

    except Exception as e:
        print(f"Login error: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()

        from src.utils.jinja_templates import templates

        html = templates.get_template("login.html").render(
            request=request, user=None, error="Ошибка входа"
        )
        return HTMLResponse(html)

    return RedirectResponse(url="/", status_code=302)


@router.get("/logout")
async def logout_page(request: Request):
    request.session.pop("user", None)
    return RedirectResponse(url="/auth/login", status_code=302)
