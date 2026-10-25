import httpx
from pydantic import BaseModel
from typing import Literal

Units = Literal[
    "teaspoons",
    "tablespoons",
    "fluid ounces",
    "cups",
    "pints",
    "quarts",
    "gallons",
    "pounds",
    "ounces",
    "inches",
    "grams",
    "milliliters",
    "liters",
    "deciliters",
    "sprigs",
    "cloves",
    "to taste",
    "whole",
    "small",
    "medium",
    "large",
]


class Ingredient(BaseModel):
    ingredient: str
    quantity: int
    units: Units
    preparation: str


class Step(BaseModel):
    ordinal: int
    instruction: str


class Recipe(BaseModel):
    title: str
    description: str | None = None
    prep_time: int | None = None
    cook_time: int | None = None
    inactive_time: int | None = None
    yield_quantity: int
    yield_units: Units
    min_servings: int | None = None
    max_servings: int | None = None
    ingredients: list[Ingredient]
    steps: list[Step]


class GetToken(BaseModel):
    token: str


class GetUser(BaseModel):
    id: int
    name: str


class Client:
    def __init__(self, host: str) -> None:
        self.host = host

    def get_token(self, username: str, password: str) -> str:
        resp = httpx.post(
            f"{self.host}/user/token",
            auth=httpx.BasicAuth(username=username, password=password),
        )
        resp.raise_for_status()

        return GetToken.model_validate(resp.json()).token

    def validate_token(self, token: str) -> tuple[bool, GetUser | None]:
        resp = httpx.get(
            f"{self.host}/user/auth",
            headers={"Authorization": f"Bearer {token}"},
        )
        if resp.status_code == httpx.codes.UNAUTHORIZED:
            return False, None
        resp.raise_for_status()
        return True, GetUser.model_validate(resp.json())

    def create_recipe(self, recipe: Recipe, token: str) -> None:
        resp = httpx.post(
            f"{self.host}/recipe",
            headers={"Authorization": f"Bearer {token}"},
            json=recipe.model_dump(mode="json"),
        )
        resp.raise_for_status()
