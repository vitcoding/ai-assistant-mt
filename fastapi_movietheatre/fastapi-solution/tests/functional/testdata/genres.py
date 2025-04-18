import uuid
from random import choice

index_ = "genres"


def generate_genres(quantity: int = 1) -> list[dict]:
    """The function of generating genres for tests."""

    genres = [
        {
            "id": str(uuid.uuid4()),
            "name": choice(("Comedy", "Fantasy", "Thriller")),
            "description": None,
        }
        for _ in range(quantity)
    ]

    return genres


genre_action = [
    {
        "id": "6c162475-c7ed-4461-9184-001ef3d9f26e",
        "name": "Action",
        "description": None,
    }
]
