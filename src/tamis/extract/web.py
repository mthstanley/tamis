from datetime import timedelta
from typing import Annotated, Literal, Union

from tamis.extract import Extractor
from urllib.parse import urlparse
import httpx
from bs4 import BeautifulSoup
from pydantic import BaseModel, Discriminator, Field, Tag, TypeAdapter
import re
from isodate import Duration, parse_duration


class HowToStep(BaseModel):
    type_name: Literal["HowToStep"] = Field(alias="@type")
    text: str | None


class HowToSection(BaseModel):
    type_name: Literal["HowToSection"] = Field(alias="@type")
    itemListElement: list[HowToStep]


class Recipe(BaseModel):
    type_name: Literal["Recipe"] = Field(alias="@type")
    name: str | None = None
    cookTime: str | None = None
    recipeIngredient: list[str] | None = None
    recipeInstructions: list[HowToStep] | HowToSection | None = None
    recipeYield: list[str] | str | None = None
    prepTime: str | None = None
    totalTime: str | None = None
    description: str | None = None


class UnknownSchema(BaseModel):
    type_name: str = Field(alias="@type")


def discriminator(v) -> str:
    type_name = v.get("@type")
    if type_name in ("Recipe"):
        return type_name
    return "unknown"


Schema = Annotated[
    Union[Annotated[Recipe, Tag("Recipe")], Annotated[UnknownSchema, Tag("unknown")]],
    Field(discriminator=Discriminator(discriminator)),
]


class Graph(BaseModel):
    items: list[Schema] = Field(alias="@graph")


JSONLDItem = Recipe | Graph
jsonld_parse_adapter = TypeAdapter(JSONLDItem)


class WebsiteExtractor(Extractor):
    def can_extract(self, url: str) -> bool:
        parsed = urlparse(url)
        if parsed.scheme != "http" and parsed.scheme != "https":
            return False

        resp = httpx.get(url)
        return 200 <= resp.status_code < 300

    def extract(self, url: str) -> str:
        resp = httpx.get(url)
        resp.raise_for_status()
        if not "html" in resp.headers.get("content-type", ""):
            return ""

        recipe = self.find_recipe_schema(resp.text)
        if recipe is None:
            return ""

        return self.format_recipe(recipe)

    def find_recipe_schema(self, html: str) -> Recipe | None:
        soup = BeautifulSoup(html, "html.parser")
        matches = soup.find_all("script", string=re.compile(r"schema\.org"))
        for match in matches:
            if match.string:
                jsonld_data = jsonld_parse_adapter.validate_json(match.string)
                match jsonld_data:
                    case Graph() as graph:
                        for item in graph.items:
                            if isinstance(item, Recipe):
                                return item
                    case Recipe() as r:
                        return r

    def duration_as_seconds(self, duration: str | None) -> int | None:
        if duration is None:
            return None
        parsed = parse_duration(duration)
        match parsed:
            case Duration():
                raise ValueError(
                    "duration contains months/years which have variable length seconds"
                )
            case timedelta() as t:
                return int(t.total_seconds())

    def format_recipe_instructions(self, recipe: Recipe) -> str:
        steps = []
        match recipe.recipeInstructions:
            case [*items] if all(isinstance(item, HowToStep) for item in items):
                steps = [step.text for step in items]
            case HowToSection(itemListElement=items):
                steps = [step.text for step in items]
        return "\n".join([f"{i + 1}. {step}" for i, step in enumerate(steps)])

    def format_recipe(self, recipe: Recipe) -> str:
        prep_time = self.duration_as_seconds(recipe.prepTime)
        cook_time = self.duration_as_seconds(recipe.cookTime)
        total_time = self.duration_as_seconds(recipe.totalTime)
        inactive_time = None
        if prep_time is not None and cook_time is not None and total_time is not None:
            inactive_time = total_time - (prep_time + cook_time)

        return (
            f"Title: {recipe.name}\n"
            f"Description: {recipe.description}\n"
            f"\nPrep Time: {prep_time} seconds\n"
            f"Cook Time: {cook_time} seconds\n"
            f"Inactive Time: {inactive_time} seconds\n"
            f"Serves: {recipe.recipeYield}\n"
            f"\n{'\n'.join(['- ' + ing for ing in recipe.recipeIngredient or []])}\n"
            f"\n{self.format_recipe_instructions(recipe)}"
        )
