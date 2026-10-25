import os
from typing import Annotated

import typer
import keyring

from tamis.extract.image import ImageExtractor
from tamis.parse.recipe import RecipeParser
from tamis.stockpot.client import Client

app = typer.Typer()

KEYRING_SERVICE_NAME = "tamis"
KEYRING_USERNAME = "stockpot"


@app.callback()
def main() -> None:
    pass


@app.command()
def login(
    username: str,
    password: Annotated[
        str, typer.Option(prompt=True, confirmation_prompt=True, hide_input=True)
    ],
    api: str = "stckpt.com",
) -> None:
    stockpot = Client(api)
    token = stockpot.get_token(username, password)
    keyring.set_password(KEYRING_SERVICE_NAME, KEYRING_USERNAME, token)
    typer.echo(f"{username} was successfully logged in")


@app.command()
def whoami(
    api: str = "stckpt.com",
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
def sift(inputs: list[str]) -> None:
    if not all(os.path.exists(i) for i in inputs):
        print("inputs must be valid file paths")
        raise typer.Exit(code=1)
    for i in inputs:
        e = ImageExtractor()
        text = e.extract(i)
        r = RecipeParser()
        extracted_data = r.parse(text)
        if extracted_data is not None:
            print(extracted_data.model_dump_json())


if __name__ == "__main__":
    app()
