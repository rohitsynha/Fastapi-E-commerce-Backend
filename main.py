import logging

from typing import List, Optional, Type

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from tortoise import BaseDBAsyncClient
from tortoise.contrib.fastapi import register_tortoise
from tortoise.signals import post_save

from authentication import generate_hashed_password, verify_token
from emailFeat import send_email
from models import Business, business_pydantic, User, user_pydantic, user_pydanticIn


logger = logging.getLogger("main")


app = FastAPI()


@post_save(User)
async def create_business(
        sender: "Type[User]",
        instance: User,
        created: bool,
        using_db: "Optional[BaseDBAsyncClient]",
        update_fields: List[str]
) -> None:

    if created:
        business_obj = await Business.create(
            name=instance.username,
            owner=instance
        )

        await business_pydantic.from_tortoise_orm(business_obj)
        await send_email([instance.email], instance)


@app.post("/registration")
async def user_registration(user: user_pydanticIn):
    info = user.dict(exclude_unset=True)
    info["password_hash"] = generate_hashed_password(info["password_hash"])
    user_obj = await User.create(**info)
    new_user = await user_pydantic.from_tortoise_orm(user_obj)

    logger.info("New User Registered: ", new_user.email)

    return {
        "status": "ok",
        "data": f"Hello {new_user.name}, Thanks for choosing our services, Please check your email inbox and click on "
                f"the link to verify your email address."
    }


templates = Jinja2Templates(directory="templates")


@app.get("/verification", response_class=HTMLResponse)
async def email_verification(request: Request, token: str):
    user = await verify_token(token)

    if user and not user.is_verified:
        user.is_verified = True
        await user.save()
        return templates.TemplateResponse("verification.html", {"request": request, "username": user.username})

    logger.warning("Invalid or expired Token, Unauthorized", user.email)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or Expired token",
        headers={
            "WWW-Authenticate": "Bearer"
        }
    )


@app.get("/")
def index():
    return {"message": "h33loworld"}


register_tortoise(
    app,
    db_url="sqlite://storage/database.sqlite3",
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True
)
