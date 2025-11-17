"""
Migración: Permitir category_id NULL en pinned_panels para soportar paneles de búsqueda global
Fecha: 2025-11-12
Versión: 1.1

Esta migración modifica la tabla pinned_panels para permitir category_id NULL,
necesario para paneles de búsqueda global que no están asociados a ninguna categoría.

SQLite no soporta ALTER COLUMN directamente, por lo que debemos:
1. Crear tabla temporal con el nuevo esquema
2. Copiar datos existentes
3. Eliminar tabla original
4. Renombrar tabla temporal
"""


def upgrade(conn):
    """Modificar pinned_panels para permitir category_id NULL"""
    print("[*] Modificando tabla pinned_panels para permitir category_id NULL...")

    cursor = conn.cursor()

    # 1. Crear tabla temporal con category_id NULL permitido
    print("    [1] Creando tabla temporal...")
    cursor.execute("""
        CREATE TABLE pinned_panels_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER,
            custom_name TEXT,
            custom_color TEXT,
            x_position INTEGER NOT NULL,
            y_position INTEGER NOT NULL,
            width INTEGER NOT NULL DEFAULT 350,
            height INTEGER NOT NULL DEFAULT 500,
            is_minimized BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_opened TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            open_count INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            filter_config TEXT DEFAULT NULL,
            keyboard_shortcut TEXT DEFAULT NULL,
            panel_type TEXT DEFAULT 'category',
            search_query TEXT DEFAULT NULL,
            advanced_filters TEXT DEFAULT NULL,
            state_filter TEXT DEFAULT 'normal',
            FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
        )
    """)

    # 2. Copiar datos existentes
    print("    [2] Copiando datos existentes...")
    cursor.execute("""
        INSERT INTO pinned_panels_new
        SELECT * FROM pinned_panels
    """)

    # 3. Eliminar tabla original
    print("    [3] Eliminando tabla original...")
    cursor.execute("DROP TABLE pinned_panels")

    # 4. Renombrar tabla temporal
    print("    [4] Renombrando tabla temporal...")
    cursor.execute("ALTER TABLE pinned_panels_new RENAME TO pinned_panels")

    conn.commit()
    print("[OK] Migración completada exitosamente")
    print("     - category_id ahora permite NULL para paneles de búsqueda global")


def downgrade(conn):
    """
    Revertir migración (recrear con category_id NOT NULL)

    ADVERTENCIA: Esto eliminará todos los paneles de búsqueda global
    con category_id = NULL
    """
    print("[!] ADVERTENCIA: Esta reversión eliminará paneles de búsqueda global")
    print("[*] Revirtiendo migración...")

    cursor = conn.cursor()

    # Eliminar paneles con category_id NULL
    cursor.execute("DELETE FROM pinned_panels WHERE category_id IS NULL")
    deleted = cursor.rowcount
    print(f"    [!] Eliminados {deleted} paneles con category_id NULL")

    # Recrear tabla con category_id NOT NULL
    cursor.execute("""
        CREATE TABLE pinned_panels_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            custom_name TEXT,
            custom_color TEXT,
            x_position INTEGER NOT NULL,
            y_position INTEGER NOT NULL,
            width INTEGER NOT NULL DEFAULT 350,
            height INTEGER NOT NULL DEFAULT 500,
            is_minimized BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_opened TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            open_count INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            filter_config TEXT DEFAULT NULL,
            keyboard_shortcut TEXT DEFAULT NULL,
            panel_type TEXT DEFAULT 'category',
            search_query TEXT DEFAULT NULL,
            advanced_filters TEXT DEFAULT NULL,
            state_filter TEXT DEFAULT 'normal',
            FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        INSERT INTO pinned_panels_new
        SELECT * FROM pinned_panels
    """)

    cursor.execute("DROP TABLE pinned_panels")
    cursor.execute("ALTER TABLE pinned_panels_new RENAME TO pinned_panels")

    conn.commit()
    print("[OK] Reversión completada")
