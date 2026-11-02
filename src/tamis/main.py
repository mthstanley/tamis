import os
from typing import Annotated

import typer
import keyring
import httpx

from tamis.extract import GeneralExtractor
from tamis.extract.web import WebsiteExtractor
from tamis.extract.image import ImageExtractor
from tamis.parse.recipe import RecipeParser
from tamis.stockpot.client import Client, Recipe

app = typer.Typer()

KEYRING_SERVICE_NAME = "tamis"
KEYRING_USERNAME = "stockpot"
STOCKPOT_API = "https://stckpt.com/api"


@app.callback()
def main() -> None:
    pass


@app.command()
def login(
    username: str,
    password: Annotated[
        str, typer.Option(prompt=True, confirmation_prompt=True, hide_input=True)
    ],
    api: str = STOCKPOT_API,
) -> None:
    stockpot = Client(api)
    token = stockpot.get_token(username, password)
    keyring.set_password(KEYRING_SERVICE_NAME, KEYRING_USERNAME, token)
    typer.echo(f"{username} was successfully logged in")


@app.command()
def whoami(
    api: str = STOCKPOT_API,
) -> None:
    stockpot = Client(api)
    token = keyring.get_password(KEYRING_SERVICE_NAME, KEYRING_USERNAME)
    if token is None:
        typer.echo("no logged in user")
        return
    valid, user = stockpot.validate_token(token)
    if not valid or user is None:
        typer.echo("token is no longer valid")
        return
    typer.echo(f"logged in as {user.name}")


@app.command()
def sift(
    inputs: list[str],
    api: str = STOCKPOT_API,
    skip_upload: bool = False,
    verbose: bool = False,
) -> None:
    token = keyring.get_password(KEYRING_SERVICE_NAME, KEYRING_USERNAME)
    if token is None:
        typer.echo("no logged in user found, please login first")
        raise typer.Exit(1)

    extractor = GeneralExtractor([ImageExtractor(), WebsiteExtractor()])
    if not all(extractor.can_extract(i) for i in inputs):
        typer.echo("unable to sift recipes from given inputs")
        raise typer.Exit(1)
    recipes: list[Recipe] = []
    recipeParser = RecipeParser()
    for i in inputs:
        text = extractor.extract(i)
        if verbose:
            typer.echo(text)
        extracted_data = recipeParser.parse(text)
        if extracted_data is not None:
            if verbose:
                typer.echo(extracted_data.model_dump_json(indent=2))
            recipes.append(extracted_data)

    stockpot = Client(api)
    if not skip_upload:
        for r in recipes:
            try:
                stockpot.create_recipe(r, token)
            except httpx.HTTPStatusError as err:
                typer.echo(
                    f"failed to create recipe: {err.response.status_code} {err.response.json()}"
                )
                raise typer.Exit(1)


if __name__ == "__main__":
    app()
