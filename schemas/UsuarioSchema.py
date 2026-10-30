from typing import Literal, Optional

from pydantic import BaseModel, Field


class UsuarioCreate(BaseModel):
    nombre: str = Field(min_length=1)
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    tipo: Literal["cliente", "administrador"]
    direccion_postal: Optional[str] = None


class UsuarioRead(BaseModel):
    id: str
    nombre: str
    email: str
    es_admin: bool
