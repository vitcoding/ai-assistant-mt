from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    """A class for work with pagination parameters."""

    page_size: int = Field(
        default=50,
        description="The number of items on the page.",
        ge=1,
    )
    page_number: int = Field(
        default=1,
        description="The page number.",
        ge=1,
    )
