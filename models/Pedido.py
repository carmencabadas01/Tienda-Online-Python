import uuid
from datetime import datetime

from models.Usuario import Cliente
from models.Producto import Producto


class Pedido:
    """Representa un pedido realizado por un cliente."""

    def __init__(
        self,
        cliente: Cliente,
        productos: list[tuple[Producto, int]]
    ):
        self.id = str(uuid.uuid4())
        self.cliente = cliente
        self.productos = productos
        self.fecha = datetime.now()

    def calcular_total(self) -> float:
        total = 0

        for producto, cantidad in self.productos:
            total += producto.precio * cantidad

        return total

    def __str__(self) -> str:
        return (
            f"Pedido de {self.cliente.nombre} - "
            f"Total: {self.calcular_total()} €"
        )