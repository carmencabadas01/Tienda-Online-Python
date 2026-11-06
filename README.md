# Tienda Online en Python

**Autora:** Carmen Cabadas

## Descripción del proyecto

Aplicación de tienda online desarrollada en Python que permite gestionar usuarios, productos y pedidos.

El proyecto incluye funcionalidades para registrar usuarios, consultar productos disponibles, gestionar el stock y realizar pedidos.

## Objetivo de la práctica

Aprender a utilizar Git y GitHub para gestionar el desarrollo de un proyecto de software mediante control de versiones, commits y ramas de trabajo.


## Docker

### Construir la imagen

```bash
docker build -t tienda-online:1.0 .
```

### Ejecutar el contenedor

```bash
docker run -p 8000:8000 tienda-online:1.0
```

Para ejecutarlo en segundo plano y con nombre:

```bash
docker run -d --name tienda -p 8000:8000 tienda-online:1.0
```

Para pararlo y eliminarlo:

```bash
docker stop tienda && docker rm tienda
```

Si el puerto 8000 está ocupado, se puede usar otro, por ejemplo `-p 8001:8000`, y entrar en `http://localhost:8001/docs`.

### Variables de entorno

La aplicación no necesita variables de entorno para funcionar.

### Pasos de prueba

1. Arranca el contenedor con el comando `docker run` anterior.
2. En la terminal debe aparecer `Uvicorn running on http://0.0.0.0:8000`.
3. Abre `http://localhost:8000/docs` en el navegador para ver la documentación interactiva (Swagger) de la API.
4. Prueba el endpoint `GET /productos` con **Try it out** y **Execute**. La respuesta esperada es código `200` y, al empezar sin datos, una lista vacía `[]`.