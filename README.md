# Boceto: App de escritorio con Python + MySQL

Este proyecto es un **boceto funcional** de una aplicación de escritorio escrita en **Python** usando **Tkinter** y conectada a **MySQL**. Implementa un CRUD sencillo para gestionar clientes.

## Requisitos

- Python 3.10 o superior
- MySQL Server activo (opcional si solo quieres la UI sin conexión a BD)
- Usuario con permisos para crear bases de datos y tablas (si usas la capa DB)

## Instalación

```bash
pip install -r requirements.txt
```

## Configuración (opcional)

Puedes sobrescribir la configuración de conexión mediante variables de entorno (Windows CMD):

```cmd
set DB_HOST=127.0.0.1
set DB_USER=root
set DB_PASSWORD=tu_password
set DB_NAME=desktop_demo
```

## Ejecución

Para lanzar la aplicación con la nueva estructura modular:

```bash
python main.py
```

Al iniciar, el script crea la base de datos y la tabla `clientes` si no existen.

## Próximos pasos

Cuando quieras, podemos mejorar el proyecto añadiendo:
- Arquitectura por capas
- Validaciones más robustas
- Búsqueda y filtros
- Empaquetado a ejecutable (`pyinstaller`)
