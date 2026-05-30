from fastapi import HTTPException, status
import httpx

from src.core import settings
from src.utils.loguru_config import AppLogger

logger = AppLogger().get_logger()


@logger.catch(reraise=True)
def async_request(
    method: str,
    url: str,
    params=None,
    data=None,
    headers=None,
    request=None,
) -> dict:
    """Вызов запроса определённого типа"""
    logger.info(f"{method = }; {url = }; {params = }; {headers = };")
    full_url = url
    if "http" not in url:
        full_url = settings.SERVER_URL + url

    final_headers = {}
    if headers:
        final_headers.update(headers)

    # Если передан request — извлекаем токен из сессии
    if request and hasattr(request, "session"):
        access_token = request.session.get("access_token")
        if access_token:
            final_headers["Authorization"] = f"Bearer {access_token}"

    with httpx.Client() as client:
        response = client.request(
            method=method,
            url=full_url,
            json=params,
            data=data,
            headers=final_headers,
        )
    logger.info(f"{response.status_code = }; {response.text = };")
    return response.json() if response.status_code != 204 else {}


def send_request(method, params, async_url, client, headers, data):
    """Отправляем запрос на клиент"""
    logger.info(f"{async_url = };")
    if method == "GET":
        result = client.get(async_url, data=data, params=params, headers=headers)
    elif method == "DELETE":
        result = client.delete(async_url, data=data, params=params, headers=headers)
    elif method == "PUT":
        result = client.put(async_url, data=data, params=params, headers=headers)
    elif method == "POST":
        result = client.post(async_url, data=data, params=params, headers=headers)
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
