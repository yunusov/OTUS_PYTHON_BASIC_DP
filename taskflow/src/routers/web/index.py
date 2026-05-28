from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from src.utils.jinja_templates import templates

router = APIRouter(tags=["Main page"])


async def get_current_user(request: Request):
    return request.session.get("user")


@router.get("/")
async def index(request: Request, user=Depends(get_current_user)):

    if user:
        html = templates.get_template("index.html").render(request=request, user=user)
    else:
        html = templates.get_template("index.html").render(request=request, user=None)

    return HTMLResponse(html)
