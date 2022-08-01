from datetime import datetime
from tortoise import Model, fields
from tortoise.contrib.pydantic import pydantic_model_creator
from pydantic import BaseModel


class User(Model):
    id = fields.IntField(pk=True, index=True)
    username = fields.CharField(max_length=20, null=False, unique=True)
    name = fields.CharField(max_length=50, null=True)
    email = fields.CharField(max_length=200, null=False, unique=True)
    password_hash = fields.CharField(max_length=100, null=False)
    is_verified = fields.BooleanField(default=False)
    join_date = fields.DatetimeField(default=datetime.utcnow)

    def __str__(self):
        return self.username

    class PydanticMeta:
        exclude = [
            "is_verified",
            "join_date"
        ]


class Business(Model):
    id = fields.IntField(pk=True, index=True)
    name = fields.CharField(max_length=20, null=False, unique=True)
    city = fields.CharField(max_length=100, null=False, default="Unspecified")
    region = fields.CharField(max_length=100, null=False, default="Unspecified")
    description = fields.TextField(null=True)
    logo = fields.CharField(max_length=200, null=False, default="defaultLogo.jpg")
    owner = fields.ForeignKeyField("models.User", related_name="business")

    def __str__(self):
        return self.name


class Product(Model):
    id = fields.IntField(pk=True, index=True)
    name = fields.CharField(max_length=100, null=False, index=True)
    category = fields.CharField(max_length=50, index=True)
    original_price = fields.DecimalField(max_digits=12, decimal_places=2)
    offer_price = fields.DecimalField(max_digits=12, decimal_places=2)
    percentage_discount = fields.IntField()
    offer_expiration_date = fields.DateField(default=datetime.utcnow)
    image = fields.CharField(max_length=200, null=False, default="defaultProductImage.jpg")
    business = fields.ForeignKeyField("models.Business", related_name='products')

    def __str__(self):
        return self.name


user_pydantic = pydantic_model_creator(User, name='User')
user_pydanticIn = pydantic_model_creator(User, name="UserIn", exclude_readonly=True)
user_pydanticOut = pydantic_model_creator(User, name="UserOut", exclude=("password_hash",))

business_pydantic = pydantic_model_creator(Business, name="Business")
business_pydanticIn = pydantic_model_creator(Business, name="BusinessIn", exclude_readonly=True)

product_pydantic = pydantic_model_creator(Product, name="Product")
product_pydanticIn = pydantic_model_creator(Product, name="ProductIn", exclude=("percentage_discount", "id"))
