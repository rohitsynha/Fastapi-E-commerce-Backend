import jwt
from fastapi import HTTPException, status
from passlib.context import CryptContext
from dotenv import dotenv_values
from models import User
import logging


logger = logging.getLogger("Authentication")


config_credentials = dotenv_values(".env")


password_context = CryptContext(schemes='bcrypt', deprecated='auto')


def generate_hashed_password(password):
    return password_context.hash(password)


async def verify_token(token: str):
    try:
        payload = jwt.decode(token, config_credentials.get("SECRET"), algorithms=["HS256"])
        user = await User.get(id=payload.get("id"))
    except Exception as e:
        logger.warning("Invalid token Exception", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )
    return user
