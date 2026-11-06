"""API REST de la tienda online (capa de exposición del servicio).

Arranque local:            uvicorn main:app --reload
Arranque para otra máquina: uvicorn main:app --host 0.0.0.0 --port 8000
Documentación interactiva:  http://localhost:8000/docs
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from Services.Tienda_service import TiendaService

from models.Usuario import Administrador
from models.Producto import ProductoElectronico, ProductoRopa

from schemas.UsuarioSchema import UsuarioCreate, UsuarioRead
from schemas.ProductoSchema import ProductoCreate, ProductoRead
from schemas.PedidoSchema import PedidoCreate, PedidoRead, PedidoItemRead

app = FastAPI(
    title="API Tienda Online",
    version="1.0.0",
    description="API REST para gestionar usuarios, productos y pedidos."
)

# CORS: permite que el frontend (abierto desde el navegador, incluso como
# fichero local o desde otro equipo) pueda llamar a la API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

tienda = TiendaService()


# ==========================================
# FUNCIONES AUXILIARES (dominio -> esquema)
# ==========================================

def convertir_usuario(usuario) -> UsuarioRead:
    return UsuarioRead(
        id=usuario.id,
        nombre=usuario.nombre,
        email=usuario.email,
        es_admin=isinstance(usuario, Administrador)
    )


def convertir_producto(producto) -> ProductoRead:
    if isinstance(producto, ProductoElectronico):
        tipo = "electronico"
    elif isinstance(producto, ProductoRopa):
        tipo = "ropa"
    else:
        tipo = "general"

    return ProductoRead(
        id=producto.id,
        tipo=tipo,
        nombre=producto.nombre,
        precio=producto.precio,
        stock=producto.stock,
        meses_garantia=getattr(producto, "garantia", None),
        talla=getattr(producto, "talla", None),
        color=getattr(producto, "color", None)
    )


def convertir_pedido(pedido) -> PedidoRead:
    return PedidoRead(
        id=pedido.id,
        fecha=pedido.fecha,
        cliente_id=pedido.cliente.id,
        total=pedido.calcular_total(),
        items=[
            PedidoItemRead(
                producto_id=producto.id,
                nombre=producto.nombre,
                cantidad=cantidad,
                precio_unitario=producto.precio,
                subtotal=producto.precio * cantidad
            )
            for producto, cantidad in pedido.productos
        ]
    )


# ==========================================
# USUARIOS
# ==========================================

@app.post("/usuarios", response_model=UsuarioRead, status_code=201)
def crear_usuario(datos: UsuarioCreate):
    usuario = tienda.registrar_usuario(
        tipo=datos.tipo,
        nombre=datos.nombre,
        email=datos.email,
        direccion=datos.direccion_postal or ""
    )

    if usuario is None:
        raise HTTPException(status_code=400, detail="Tipo de usuario no válido")

    return convertir_usuario(usuario)


@app.get("/usuarios", response_model=list[UsuarioRead])
def listar_usuarios():
    return [convertir_usuario(u) for u in tienda.usuarios]


@app.get("/usuarios/{usuario_id}", response_model=UsuarioRead)
def obtener_usuario(usuario_id: str):
    usuario = tienda.buscar_usuario(usuario_id)

    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return convertir_usuario(usuario)


# ==========================================
# PRODUCTOS
# ==========================================
# La validación de cada tipo (electrónico necesita garantía, ropa necesita
# talla y color, precio > 0, stock >= 0...) la hace el esquema ProductoCreate;
# si los datos no son válidos FastAPI responde automáticamente 422.

@app.post("/productos", response_model=ProductoRead, status_code=201)
def crear_producto(datos: ProductoCreate):
    if datos.tipo == "electronico":
        producto = tienda.anadir_producto(
            tipo="electronico",
            nombre=datos.nombre,
            precio=datos.precio,
            stock=datos.stock,
            garantia=datos.meses_garantia
        )
    elif datos.tipo == "ropa":
        producto = tienda.anadir_producto(
            tipo="ropa",
            nombre=datos.nombre,
            precio=datos.precio,
            stock=datos.stock,
            talla=datos.talla,
            color=datos.color
        )
    else:
        producto = tienda.anadir_producto(
            tipo="general",
            nombre=datos.nombre,
            precio=datos.precio,
            stock=datos.stock
        )

    return convertir_producto(producto)


@app.get("/productos", response_model=list[ProductoRead])
def listar_productos():
    return [convertir_producto(p) for p in tienda.productos]


@app.get("/productos/{producto_id}", response_model=ProductoRead)
def obtener_producto(producto_id: str):
    producto = tienda.buscar_producto(producto_id)

    if producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    return convertir_producto(producto)


@app.delete("/productos/{producto_id}", status_code=204)
def eliminar_producto(producto_id: str):
    if not tienda.eliminar_producto(producto_id):
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    return None


# ==========================================
# PEDIDOS
# ==========================================

@app.post("/pedidos", response_model=PedidoRead, status_code=201)
def crear_pedido(datos: PedidoCreate):
    # 1) El cliente debe existir
    if tienda.buscar_usuario(datos.cliente_id) is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    # 2) Se agrupan las líneas repetidas del mismo producto
    cantidades = {}
    for item in datos.items:
        cantidades[item.producto_id] = (
            cantidades.get(item.producto_id, 0) + item.cantidad
        )

    # 3) Cada producto debe existir y tener stock suficiente
    for producto_id, cantidad in cantidades.items():
        producto = tienda.buscar_producto(producto_id)

        if producto is None:
            raise HTTPException(
                status_code=404,
                detail=f"Producto {producto_id} no encontrado"
            )

        if not producto.hay_stock(cantidad):
            raise HTTPException(
                status_code=409,
                detail=(
                    f"Stock insuficiente para '{producto.nombre}': "
                    f"disponible {producto.stock}, solicitado {cantidad}"
                )
            )

    # 4) Se crea el pedido con la lógica de TiendaService
    pedido = tienda.realizar_pedido(
        usuario_id=datos.cliente_id,
        productos_pedido=list(cantidades.items())
    )

    if pedido is None:
        raise HTTPException(
            status_code=400,
            detail="No se ha podido crear el pedido"
        )

    return convertir_pedido(pedido)


@app.get("/usuarios/{usuario_id}/pedidos", response_model=list[PedidoRead])
def listar_pedidos_usuario(usuario_id: str):
    if tienda.buscar_usuario(usuario_id) is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return [
        convertir_pedido(p)
        for p in tienda.listar_pedidos_usuario(usuario_id)
    ]
