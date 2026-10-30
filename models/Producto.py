import uuid


class Producto:
    """Clase base para los productos de la tienda."""

    def __init__(self, nombre: str, precio: float, stock: int):
        self.id = str(uuid.uuid4())
        self.nombre = nombre
        self.precio = precio
        self.stock = stock

    def hay_stock(self, cantidad: int) -> bool:
        return self.stock >= cantidad

    def actualizar_stock(self, cantidad: int) -> None:
        self.stock += cantidad

    def __str__(self) -> str:
        return (
            f"ID: {self.id}, nombre: {self.nombre}, "
            f"precio: {self.precio}, stock: {self.stock}"
        )


class ProductoElectronico(Producto):
    """Producto electrónico con garantía."""

    def __init__(
        self,
        nombre: str,
        precio: float,
        stock: int,
        garantia: int
    ):
        super().__init__(nombre, precio, stock)
        self.garantia = garantia

    def __str__(self) -> str:
        return f"{super().__str__()}, garantía: {self.garantia} meses"


class ProductoRopa(Producto):
    """Producto de ropa con talla y color."""

    def __init__(
        self,
        nombre: str,
        precio: float,
        stock: int,
        talla: str,
        color: str
    ):
        super().__init__(nombre, precio, stock)
        self.talla = talla
        self.color = color

    def __str__(self) -> str:
        return (
            f"{super().__str__()}, talla: {self.talla}, "
            f"color: {self.color}"
        )