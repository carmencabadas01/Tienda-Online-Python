"""Cliente Python de la API de la tienda online (usa solo HTTP con requests).

Este script es independiente de la aplicación FastAPI: no importa
TiendaService, ni los modelos, ni nada del servidor.

Uso:
    python cliente.py                          # API en localhost:8000
    python cliente.py http://192.168.1.34:8000 # API en otro equipo
    (también se puede definir la variable de entorno BASE_URL)
"""
import os
import sys

import requests

# Dirección base de la API. Se puede cambiar editando esta línea, pasando la
# URL como argumento o definiendo la variable de entorno BASE_URL.
BASE_URL = "http://localhost:8000"

if len(sys.argv) > 1:
    BASE_URL = sys.argv[1]
elif os.environ.get("BASE_URL"):
    BASE_URL = os.environ["BASE_URL"]

BASE_URL = BASE_URL.rstrip("/")
TIMEOUT = 5  # segundos


class ErrorAPI(Exception):
    """La API respondió con un código de estado distinto del esperado."""


def peticion(titulo, metodo, ruta, esperado, **kwargs):
    """Envía una petición, comprueba el código HTTP y devuelve el JSON."""
    print(f"\n=== {titulo} ===")
    print(f"{metodo} {BASE_URL}{ruta}")

    respuesta = requests.request(
        metodo, f"{BASE_URL}{ruta}", timeout=TIMEOUT, **kwargs
    )

    print(f"Código recibido: {respuesta.status_code} (esperado: {esperado})")

    try:
        datos = respuesta.json()
    except ValueError:
        datos = None

    if respuesta.status_code != esperado:
        raise ErrorAPI(f"{titulo}: la API respondió con error -> {datos}")

    print("Respuesta JSON:", datos)
    return datos


def comprobar_error(titulo, metodo, ruta, esperado, **kwargs):
    """Provoca un error a propósito y comprueba que la API lo rechaza."""
    print(f"\n=== {titulo} ===")
    respuesta = requests.request(
        metodo, f"{BASE_URL}{ruta}", timeout=TIMEOUT, **kwargs
    )
    resultado = "OK" if respuesta.status_code == esperado else "INESPERADO"
    print(
        f"{metodo} {ruta} -> {respuesta.status_code} "
        f"(esperado {esperado}) [{resultado}]"
    )
    try:
        print("Detalle:", respuesta.json())
    except ValueError:
        pass


def main():
    print(f"Probando la API en {BASE_URL}")

    # 1. Crear un usuario
    usuario = peticion(
        "CREAR USUARIO", "POST", "/usuarios", 201,
        json={
            "nombre": "Ana",
            "email": "ana@gmail.com",
            "tipo": "cliente",
            "direccion_postal": "Calle Mayor 10, Vigo"
        }
    )
    usuario_id = usuario["id"]

    # 2. Consultar la lista de usuarios
    usuarios = peticion("LISTAR USUARIOS", "GET", "/usuarios", 200)
    print(f"-> Hay {len(usuarios)} usuario(s) registrado(s)")

    # 3. Crear varios productos (electrónico, ropa y general)
    portatil = peticion(
        "CREAR PRODUCTO ELECTRÓNICO", "POST", "/productos", 201,
        json={
            "tipo": "electronico", "nombre": "Ordenador portátil",
            "precio": 899.99, "stock": 10, "meses_garantia": 24
        }
    )
    camiseta = peticion(
        "CREAR PRODUCTO DE ROPA", "POST", "/productos", 201,
        json={
            "tipo": "ropa", "nombre": "Camiseta",
            "precio": 19.95, "stock": 30, "talla": "M", "color": "Negro"
        }
    )
    peticion(
        "CREAR PRODUCTO GENERAL", "POST", "/productos", 201,
        json={
            "tipo": "general", "nombre": "Mochila",
            "precio": 39.5, "stock": 12
        }
    )

    # 4. Consultar la lista de productos
    productos = peticion("LISTAR PRODUCTOS", "GET", "/productos", 200)
    print(f"-> Hay {len(productos)} producto(s) en la tienda")

    # 5. Crear un pedido para el usuario
    pedido = peticion(
        "CREAR PEDIDO", "POST", "/pedidos", 201,
        json={
            "cliente_id": usuario_id,
            "items": [
                {"producto_id": portatil["id"], "cantidad": 1},
                {"producto_id": camiseta["id"], "cantidad": 2}
            ]
        }
    )
    print(f"-> Total del pedido: {pedido['total']:.2f} €")

    # 6. Consultar los pedidos realizados por dicho usuario
    pedidos = peticion(
        "PEDIDOS DEL USUARIO", "GET", f"/usuarios/{usuario_id}/pedidos", 200
    )
    print(f"-> El usuario tiene {len(pedidos)} pedido(s)")

    # Comprobación del stock tras el pedido
    portatil_actual = peticion(
        "STOCK DEL PORTÁTIL TRAS EL PEDIDO",
        "GET", f"/productos/{portatil['id']}", 200
    )
    print(f"-> Stock actual: {portatil_actual['stock']} (antes: 10)")

    # Casos de error: la API debe rechazarlos con el código adecuado
    print("\n##### COMPROBACIÓN DE ERRORES #####")
    comprobar_error(
        "Pedido con cliente inexistente", "POST", "/pedidos", 404,
        json={"cliente_id": "no-existe",
              "items": [{"producto_id": camiseta["id"], "cantidad": 1}]}
    )
    comprobar_error(
        "Pedido con producto inexistente", "POST", "/pedidos", 404,
        json={"cliente_id": usuario_id,
              "items": [{"producto_id": "no-existe", "cantidad": 1}]}
    )
    comprobar_error(
        "Pedido sin stock suficiente", "POST", "/pedidos", 409,
        json={"cliente_id": usuario_id,
              "items": [{"producto_id": portatil["id"], "cantidad": 999}]}
    )
    comprobar_error(
        "Producto con datos no válidos", "POST", "/productos", 422,
        json={"tipo": "electronico", "nombre": "Sin garantía",
              "precio": 10, "stock": 1}
    )

    print("\nPrueba completada correctamente.")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print(
            f"\nNo se ha podido conectar con {BASE_URL}.\n"
            "Comprueba que el servidor está arrancado, que la IP/puerto son "
            "correctos y, si es otro equipo, que se inició con --host 0.0.0.0 "
            "y que el cortafuegos permite el puerto."
        )
        sys.exit(1)
    except requests.exceptions.Timeout:
        print(f"\nTiempo de espera agotado al conectar con {BASE_URL}.")
        sys.exit(1)
    except ErrorAPI as error:
        print(f"\nERROR: {error}")
        sys.exit(1)
