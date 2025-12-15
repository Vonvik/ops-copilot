from pydantic import BaseModel, Field, field_validator


class Item(BaseModel):
    name: str = Field(..., min_length=1, description="Item name")
    price: float = Field(..., gt=0, description="Price must be > 0")

    @field_validator("name")
    @classmethod
    def name_trim(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("name cannot be empty")
        return v


class ItemOut(Item):
    id: int
