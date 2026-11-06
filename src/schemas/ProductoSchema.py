from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator


class ProductoCreate(BaseModel):
    tipo: Literal["general", "electronico", "ropa"]
    nombre: str = Field(min_length=1)
    precio: float = Field(gt=0)
    stock: int = Field(ge=0)
    meses_garantia: Optional[int] = Field(default=None, gt=0)
    talla: Optional[str] = None
    color: Optional[str] = None

    @model_validator(mode="after")
    def validar_atributos_segun_tipo(self):
        if self.tipo == "electronico" and self.meses_garantia is None:
            raise ValueError(
                "Los productos electrónicos requieren 'meses_garantia'"
            )

        if self.tipo == "ropa" and (not self.talla or not self.color):
            raise ValueError(
                "Los productos de ropa requieren 'talla' y 'color'"
            )

        return self


class ProductoRead(BaseModel):
    id: str
    tipo: str
    nombre: str
    precio: float
    stock: int
    meses_garantia: Optional[int] = None
    talla: Optional[str] = None
    color: Optional[str] = None
