from pydantic import BaseModel, Field


class ItemResponseSchema(BaseModel):
    code: str = Field(..., description="Code of the item")
    brand: str = Field(..., description="Brand of the item")
    description: str = Field(..., description="Description of the item")
    isBox: bool = Field(..., description="Is the item a box?")
    dimension: str = Field(..., description="Dimension of the item")
    quantity: int = Field(..., description="Quantity of the item")
    price: int = Field(..., description="Cost of the item")

    class Config:
        from_attributes = True
        orm_mode = True


class ItemRequestSchema(ItemResponseSchema):
    pass

