import os
import mysql.connector
from mysql.connector import Error as MySQLError

DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '1234')
DB_NAME = os.getenv('DB_NAME', 'desktop_demo')


def get_server_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
    )


def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
    )


def test_connection():
    """Prueba la conexión a MySQL y devuelve True si funciona."""
    try:
        conn = get_server_connection()
        conn.close()
        return True
    except MySQLError:
        return False


def ensure_database():
    """Crea la base de datos y las tablas si no existen."""
    try:
        server_conn = get_server_connection()
        cur = server_conn.cursor()
        cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        cur.close()
        server_conn.close()

        db_conn = get_db_connection()
        cur = db_conn.cursor()

        # Tabla de turnos
        cur.execute('''
            CREATE TABLE IF NOT EXISTS turnos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                turno VARCHAR(10) NOT NULL,
                alumno VARCHAR(150) NOT NULL,
                facultad VARCHAR(100) NOT NULL,
                asesor VARCHAR(100) NOT NULL,
                hora VARCHAR(10) NOT NULL,
                estado VARCHAR(20) NOT NULL DEFAULT 'espera'
            )
        ''')

        # Tabla de cubículos (cada uno asignado a un asesor)
        cur.execute('''
            CREATE TABLE IF NOT EXISTS cubiculos (
                id VARCHAR(10) PRIMARY KEY,
                asesor VARCHAR(100) NOT NULL DEFAULT 'Sin asignar',
                estado VARCHAR(20) NOT NULL DEFAULT 'Libre'
            )
        ''')

        # Migración: agregar columna asesor si no existe (tabla antigua)
        try:
            cur.execute("ALTER TABLE cubiculos ADD COLUMN asesor VARCHAR(100) NOT NULL DEFAULT 'Sin asignar' AFTER id")
        except MySQLError:
            pass

        # Tabla de asesores
        cur.execute('''
            CREATE TABLE IF NOT EXISTS asesores (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL UNIQUE,
                cubiculo VARCHAR(10) DEFAULT NULL,
                FOREIGN KEY (cubiculo) REFERENCES cubiculos(id) ON DELETE SET NULL
            )
        ''')

        # Migración: agregar columna cubiculo si no existe
        try:
            cur.execute("ALTER TABLE asesores ADD COLUMN cubiculo VARCHAR(10) DEFAULT NULL AFTER nombre")
        except MySQLError:
            pass

        db_conn.commit()
        cur.close()
        db_conn.close()
        return True
    except MySQLError as e:
        print(f"Error BD: {e}")
        return False


# ========== CRUD Asesores (con cubiculo asignado) ==========

def insertar_asesor(nombre, cubiculo_id=None):
    """
    Agrega un nuevo asesor y le asigna un cubículo.
    Si cubiculo_id se proporciona, también actualiza la tabla cubiculos.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Insertar asesor (con cubiculo si se proporcionó)
        if cubiculo_id:
            cur.execute(
                "INSERT IGNORE INTO asesores (nombre, cubiculo) VALUES (%s, %s)",
                (nombre, cubiculo_id)
            )
            # Asignar el cubículo al asesor
            cur.execute(
                "UPDATE cubiculos SET asesor = %s WHERE id = %s",
                (nombre, cubiculo_id)
            )
        else:
            cur.execute(
                "INSERT IGNORE INTO asesores (nombre) VALUES (%s)",
                (nombre,)
            )

        conn.commit()
        inserted = cur.rowcount > 0
        cur.close()
        conn.close()
        return inserted
    except MySQLError:
        return False


def obtener_asesores():
    """Devuelve lista de dicts con nombre y cubiculo de cada asesor."""
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT nombre, cubiculo FROM asesores ORDER BY id ASC")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows  # [{"nombre": "...", "cubiculo": "..."}, ...]
    except MySQLError:
        return []


def obtener_asesores_nombres():
    """Devuelve solo lista de nombres de asesores."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT nombre FROM asesores ORDER BY id ASC")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [row[0] for row in rows]
    except MySQLError:
        return []


def eliminar_asesor(nombre):
    """
    Elimina un asesor y libera su cubículo (lo pone como 'Sin asignar').
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Obtener el cubiculo del asesor antes de eliminarlo
        cur.execute("SELECT cubiculo FROM asesores WHERE nombre = %s", (nombre,))
        row = cur.fetchone()
        cubiculo_id = row[0] if row else None

        # Eliminar asesor
        cur.execute("DELETE FROM asesores WHERE nombre = %s", (nombre,))
        deleted = cur.rowcount > 0

        # Liberar el cubículo
        if cubiculo_id:
            cur.execute(
                "UPDATE cubiculos SET asesor = 'Sin asignar' WHERE id = %s",
                (cubiculo_id,)
            )

        conn.commit()
        cur.close()
        conn.close()
        return deleted
    except MySQLError:
        return False


def obtener_cubiculos_disponibles():
    """Devuelve lista de (id, asesor) de cubículos sin asesor o con asesor 'Sin asignar'."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, asesor FROM cubiculos WHERE asesor = 'Sin asignar' ORDER BY id ASC")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows
    except MySQLError:
        return []


# ========== CRUD Cubículos ==========

def insertar_cubiculo(cubiculo_id, asesor="Sin asignar"):
    """Agrega un nuevo cubículo."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT IGNORE INTO cubiculos (id, asesor, estado) VALUES (%s, %s, 'Libre')",
            (cubiculo_id, asesor)
        )
        conn.commit()
        inserted = cur.rowcount > 0
        cur.close()
        conn.close()
        return inserted
    except MySQLError:
        return False


def eliminar_cubiculo(cubiculo_id):
    """Elimina un cubículo (libera el asesor que lo tenía)."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Desvincular de cualquier asesor
        cur.execute("UPDATE asesores SET cubiculo = NULL WHERE cubiculo = %s", (cubiculo_id,))
        # Eliminar el cubículo
        cur.execute("DELETE FROM cubiculos WHERE id = %s", (cubiculo_id,))
        conn.commit()
        deleted = cur.rowcount > 0
        cur.close()
        conn.close()
        return deleted
    except MySQLError:
        return False


def inicializar_cubiculos(cubiculos_dict):
    """
    Inserta los cubículos por primera vez si no existen.
    cubiculos_dict: {id: asesor}
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        for cub_id, asesor in cubiculos_dict.items():
            cur.execute(
                "INSERT IGNORE INTO cubiculos (id, asesor, estado) VALUES (%s, %s, 'Libre')",
                (cub_id, asesor)
            )
        conn.commit()
        cur.close()
        conn.close()
    except MySQLError:
        pass


def actualizar_estado_cubiculo(cubiculo_id, nuevo_estado):
    """Actualiza el estado de un cubículo."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE cubiculos SET estado = %s WHERE id = %s",
            (nuevo_estado, cubiculo_id)
        )
        conn.commit()
        cur.close()
        conn.close()
    except MySQLError:
        pass


def obtener_estados_cubiculos():
    """Devuelve un dict {cubiculo_id: {'estado': ..., 'asesor': ...}}."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, estado, asesor FROM cubiculos")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return {row[0]: {"estado": row[1], "asesor": row[2]} for row in rows}
    except MySQLError:
        return {}


def actualizar_asesor_cubiculo(cubiculo_id, asesor):
    """Actualiza el asesor asignado a un cubículo."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE cubiculos SET asesor = %s WHERE id = %s",
            (asesor, cubiculo_id)
        )
        conn.commit()
        cur.close()
        conn.close()
    except MySQLError:
        pass


def obtener_cubiculos_completos():
    """Devuelve lista de (id, asesor, estado) de todos los cubículos."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, asesor, estado FROM cubiculos ORDER BY id ASC")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows
    except MySQLError:
        return []


# ========== CRUD Turnos ==========

def insertar_turno(turno, alumno, facultad, asesor, hora):
    """Guarda un nuevo turno en la BD."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO turnos (turno, alumno, facultad, asesor, hora, estado) VALUES (%s, %s, %s, %s, %s, 'espera')",
            (turno, alumno, facultad, asesor, hora)
        )
        conn.commit()
        cur.close()
        conn.close()
        return True
    except MySQLError:
        return False


def obtener_turnos_espera():
    """Devuelve los turnos en espera ordenados por id."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT turno, alumno, facultad, asesor, hora FROM turnos WHERE estado = 'espera' ORDER BY id ASC"
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows
    except MySQLError:
        return []


def obtener_turno_por_id_bd(turno):
    """
    Busca un turno por su código (ej. 'T01') y devuelve su id interno y datos.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT id, turno, alumno, asesor FROM turnos WHERE turno = %s AND estado = 'espera' LIMIT 1",
            (turno,)
        )
        row = cur.fetchone()
        cur.close()
        conn.close()
        return row
    except MySQLError:
        return None


def llamar_turno_especifico(turno):
    """
    Marca un turno específico como 'atendido' y lo devuelve.
    turno: el código del turno (ej. 'T01')
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)

        cur.execute(
            "SELECT id, turno, alumno, asesor FROM turnos WHERE turno = %s AND estado = 'espera' LIMIT 1",
            (turno,)
        )
        row = cur.fetchone()
        if row:
            cur.execute("UPDATE turnos SET estado = 'atendido' WHERE id = %s", (row["id"],))
            conn.commit()
            cur.close()
            conn.close()
            return {"turno": row["turno"], "alumno": row["alumno"], "asesor": row["asesor"]}
        cur.close()
        conn.close()
        return None
    except MySQLError:
        return None


def llamar_siguiente_turno():
    """Marca el primer turno en espera como 'atendido' y lo devuelve."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, turno, alumno, asesor FROM turnos WHERE estado = 'espera' ORDER BY id ASC LIMIT 1"
        )
        row = cur.fetchone()
        if row:
            cur.execute("UPDATE turnos SET estado = 'atendido' WHERE id = %s", (row[0],))
            conn.commit()
            cur.close()
            conn.close()
            return {"turno": row[1], "alumno": row[2], "asesor": row[3]}
        cur.close()
        conn.close()
        return None
    except MySQLError:
        return None


def contar_turnos_espera():
    """Cuenta cuántos turnos hay en espera."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM turnos WHERE estado = 'espera'")
        count = cur.fetchone()[0]
        cur.close()
        conn.close()
        return count
    except MySQLError:
        return 0