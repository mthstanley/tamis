import os

import typer

from tamis.extract.image import ImageExtractor
from tamis.parse.recipe import RecipeParser

app = typer.Typer()


@app.callback()
def main() -> None:
    pass


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
