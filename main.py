import tkinter as tk
from ui import SCA_App
from db import test_connection, ensure_database


def main():
    # Probar conexión MySQL
    mysql_disponible = test_connection()
    
    if mysql_disponible:
        print("✓ MySQL conectado. Creando base de datos y tablas si es necesario...")
        ensure_database()
    else:
        print("⚠ MySQL no disponible. La aplicación funcionará en modo local (sin BD).")
    
    root = tk.Tk()
    app = SCA_App(root, mysql_disponible)
    root.mainloop()


if __name__ == "__main__":
    main()
