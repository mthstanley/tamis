import ollama
from tamis.stockpot.client import Recipe, Ingredient, Step


class RecipeParser:
    def parse(self, text: str) -> Recipe | None:
        response = ollama.chat(
            model="llama3.2",
            messages=[
                {
                    "role": "system",
                    "content": """

                    You are a helpful assistant designed to extract the
                    relevant information from the text of a recipe and output
                    it as structure json.

                    # Ingredients

                    When extracting ingredients make sure to extract all words
                    that are part of the ingredient line, do not combine with
                    text elsewhere in the recipe. For example do not pull
                    preparation from anywhere in the recipe except the
                    ingredient list.

                    If quantity is not present use 0.

                    For units use "whole" when there is a quantity but no unit
                    in the text. When there is no quantity or units given use
                    "to taste".

                    # Steps

                    When extracting instructions these are typically preceded
                    by bullet points or numbers or some other marker, if not
                    present then seaprate paragraphs can be a good marker.
                    Always extract the full text from each step.

                    # Recipe Metadata

                    The recipe description is typically text that is not an
                    ingredient or a step and describes the dish. It is
                    typically found at the beginning of the recipe. Always
                    extract the full text for the description.

                    All times extracted should be converted to seconds.

                    """,
                },
                {
                    "role": "user",
                    "content": """

                    Extract the recipe information from this text:

                    Carrot Soup

                    Serves 5 to 10
                    Prep: 30 mins Inactive: 1 hour 30 mins

                    A warming buttery carrot soup.

                    2 carrots, peeled and diced
                    1 onion, diced
                    3 cloves of garlic (1 minced, 2 smashed)
                    1 sprig fresh rosemary
                    1 tablespoon minced sundried tomatoes
                    2 tablespoons butter, softened
                    2 15oz cans chicken broth
                    salt & pepper

                    1. Melt the butter over medium heat.
                       Stir in onion and cook until translucent.
                    2. Add the garlic and stir until fragrant, 30 seconds.
                    3. Saute the carrots until tender.
                    4. Add the broth and rosemary and simmer for 30 minutes.
                    5. Season to taste with salt and pepper.

                    """,
                },
                {
                    "role": "assistant",
                    "content": Recipe(
                        title="Carrot Soup",
                        description="A warming buttery carrot soup.",
                        prep_time=1800,
                        inactive_time=5400,
                        yield_quantity=0,
                        yield_units="grams",
                        ingredients=[
                            Ingredient(
                                ingredient="carrots",
                                quantity=2,
                                units="whole",
                                preparation="peeled and diced",
                            ),
                            Ingredient(
                                ingredient="onion",
                                quantity=1,
                                units="whole",
                                preparation="diced",
                            ),
                            Ingredient(
                                ingredient="garlic",
                                quantity=3,
                                units="cloves",
                                preparation="1 minced, 2 smashed",
                            ),
                            Ingredient(
                                ingredient="fresh rosemary",
                                quantity=1,
                                units="sprigs",
                                preparation="",
                            ),
                            Ingredient(
                                ingredient="butter",
                                quantity=2,
                                units="tablespoons",
                                preparation="softened",
                            ),
                            Ingredient(
                                ingredient="sundried tomatoes",
                                quantity=1,
                                units="tablespoons",
                                preparation="minced",
                            ),
                            Ingredient(
                                ingredient="chicken broth",
                                quantity=30,
                                units="ounces",
                                preparation="15oz cans",
                            ),
                            Ingredient(
                                ingredient="salt",
                                quantity=0,
                                units="to taste",
                                preparation="",
                            ),
                            Ingredient(
                                ingredient="pepper",
                                quantity=0,
                                units="to taste",
                                preparation="",
                            ),
                        ],
                        steps=[
                            Step(
                                ordinal=1,
                                instruction="Melt the butter over medium heat. Stir in onion and cook until translucent.",
                            ),
                            Step(
                                ordinal=2,
                                instruction="Add the garlic and stir until fragrant, 30 seconds.",
                            ),
                            Step(
                                ordinal=3, instruction="Saute the carrots until tender."
                            ),
                            Step(
                                ordinal=4,
                                instruction="Add the broth and rosemary and simmer for 30 minutes.",
                            ),
                            Step(
                                ordinal=5,
                                instruction="Season to taste with salt and pepper.",
                            ),
                        ],
                    ).model_dump_json(),
                },
                {
                    "role": "user",
                    "content": f"Extract the recipe information from this text: {text}",
                },
            ],
            format=Recipe.model_json_schema(),
            options={"temperature": 0.0},
        )

        if response.message.content is None:
            return None

        return Recipe.model_validate_json(response.message.content)
