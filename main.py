from fastapi import FastAPI
import uvicorn

from src.utils.loguru_config import AppLogger


logger = AppLogger().get_logger()
app = FastAPI()

if __name__ == "__main__":
    logger.info("APP started!!!")
    uvicorn.run("main:app", reload=True)