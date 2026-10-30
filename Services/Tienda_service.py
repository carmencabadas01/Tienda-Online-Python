from models.Usuario import Cliente, Administrador
from models.Producto import Producto, ProductoElectronico, ProductoRopa
from models.Pedido import Pedido


class TiendaService:
    """Gestiona las operaciones principales de la tienda."""

    def __init__(self):
        self.usuarios = []
        self.productos = []
        self.pedidos = []

    # ---------------- USUARIOS ----------------

    def registrar_usuario(
        self,
        tipo: str,
        nombre: str,
        email: str,
        direccion: str = ""
    ):
        if tipo == "cliente":
            usuario = Cliente(nombre, email, direccion)
        elif tipo == "administrador":
            usuario = Administrador(nombre, email)
        else:
            return None

        self.usuarios.append(usuario)
        return usuario

    def buscar_usuario(self, usuario_id: str):
        for usuario in self.usuarios:
            if usuario.id == usuario_id:
                return usuario

        return None

    # ---------------- PRODUCTOS ----------------

    def anadir_producto(
        self,
        tipo: str,
        nombre: str,
        precio: float,
        stock: int,
        **kwargs
    ):
        if tipo == "electronico":
            producto = ProductoElectronico(
                nombre,
                precio,
                stock,
                kwargs["garantia"]
            )
        elif tipo == "ropa":
            producto = ProductoRopa(
                nombre,
                precio,
                stock,
                kwargs["talla"],
                kwargs["color"]
            )
        else:
            producto = Producto(nombre, precio, stock)

        self.productos.append(producto)
        return producto

    def eliminar_producto(self, producto_id: str) -> bool:
        for producto in self.productos:
            if producto.id == producto_id:
                self.productos.remove(producto)
                return True

        return False

    def listar_productos(self) -> None:
        for producto in self.productos:
            print(producto)

    def buscar_producto(self, producto_id: str):
        for producto in self.productos:
            if producto.id == producto_id:
                return producto

        return None

    # ---------------- PEDIDOS ----------------

    def realizar_pedido(
        self,
        usuario_id: str,
        productos_pedido: list[tuple[str, int]]
    ):
        """Crea un pedido. Devuelve None si el cliente no existe, algún
        producto no existe, alguna cantidad no es válida o no hay stock
        suficiente. No modifica el stock si el pedido no se puede crear."""
        usuario = self.buscar_usuario(usuario_id)

        if usuario is None or not productos_pedido:
            return None

        # Se agrupan las líneas repetidas del mismo producto para comprobar
        # el stock sobre la cantidad total pedida.
        cantidades = {}

        for producto_id, cantidad in productos_pedido:
            if cantidad <= 0:
                return None
            cantidades[producto_id] = cantidades.get(producto_id, 0) + cantidad

        productos_seleccionados = []

        for producto_id, cantidad in cantidades.items():
            producto = self.buscar_producto(producto_id)

            if producto is None or not producto.hay_stock(cantidad):
                return None

            productos_seleccionados.append((producto, cantidad))

        for producto, cantidad in productos_seleccionados:
            producto.actualizar_stock(-cantidad)

        pedido = Pedido(usuario, productos_seleccionados)
        self.pedidos.append(pedido)

        return pedido

    def listar_pedidos_usuario(self, usuario_id: str) -> list[Pedido]:
        pedidos_usuario = []

        for pedido in self.pedidos:
            if pedido.cliente.id == usuario_id:
                pedidos_usuario.append(pedido)

        pedidos_usuario.sort(key=lambda pedido: pedido.fecha)

        return pedidos_usuario
