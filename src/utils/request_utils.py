from fastapi import HTTPException, status
import httpx

from src.config import settings
from src.utils.loguru_config import AppLogger

logger = AppLogger().get_logger()


@logger.catch(reraise=True)
async def async_request(method: str, url: str, params=None) -> str:
    """Вызов запроса определённого типа"""
    logger.info(f"{method = }; {url = }; {params = };")
    async_url = url
    if "http" not in url:
        async_url = settings.SERVER_URL + url

    async with httpx.AsyncClient() as client:
        result = await send_request(method, params, async_url, client)
        if result.is_error:
            return make_error_msg(result)
        return result.json()

async def send_request(method, params, async_url, client):
    """Отправляем запрос на клиент"""
    if method.upper() == "GET":
        result = await client.get(async_url, params=params)
    elif method.upper() == "DELETE":
        result = await client.delete(async_url, params=params)
    elif method.upper() == "PUT":
        result = await client.put(async_url, params=params)
    elif method.upper() == "POST":
        result = await client.post(async_url, params=params)
    else:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неопознанный метод запроса '{method}'",
            )   
    return result

def make_error_msg(result) -> dict:
    """Создать сообщение об ошибке"""
    logger.error(f"API error {result.status_code}: {result.text}")
    try:
        error_data = result.json()
        error_msg = {
            "error_message": error_data.get(
                "detail", error_data.get("message", result.text)
            )
        }
        logger.info(error_msg)
        return error_msg
    except Exception:
        error_msg = {"error_message": result.text}
        logger.info(error_msg)
        return error_msg