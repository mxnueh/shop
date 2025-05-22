import pyodbc

conn = pyodbc.connect(
        r'DRIVER={ODBC Driver 17 for SQL Server};'
        r'SERVER=DESKTOP-EK6KQLL\MSSQLSERVER_2022;'
        r'DATABASE=notificaciones;'
        r'Trusted_Connection=yes;'
    )

cursor = conn.cursor()

# --- Funciones de sistema ---

def agregar_usuario():
    nombre = input("Nombre del usuario: ")
    correo = input("Correo del usuario: ")
    es_admin = input("¿Es administrador? (s/n): ").lower() == 's'
    cursor.execute("""
        INSERT INTO Usuarios (Nombre, Correo, EsAdministrador)
        VALUES (?, ?, ?)
    """, (nombre, correo, int(es_admin)))
    conn.commit()
    print("✅ Usuario agregado.")

def crear_y_enviar_notificacion():
    id_remitente = int(input("ID del administrador que envía: "))
    titulo = input("Título de la notificación: ")
    mensaje = input("Mensaje: ")

    # Insertar notificación y obtener el ID generado
    cursor.execute("""
        INSERT INTO Notificaciones (Titulo, Mensaje, IdRemitente)
        OUTPUT INSERTED.Id
        VALUES (?, ?, ?)
    """, (titulo, mensaje, id_remitente))
    
    # Obtener el ID de la notificación recién insertada
    id_notificacion = cursor.fetchone()[0]
    conn.commit()
    
    print(f"Notificación creada con ID: {id_notificacion}")

    ids = input("IDs de destinatarios separados por coma (ej: 2,3,4): ")
    id_usuarios = [int(i.strip()) for i in ids.split(',')]

    # Insertar las relaciones usuario-notificación
    for id_usuario in id_usuarios:
        cursor.execute("""
            INSERT INTO UsuarioNotificacion (IdUsuario, IdNotificacion)
            VALUES (?, ?)
        """, (id_usuario, id_notificacion))
    
    conn.commit()
    print("📨 Notificación enviada a todos los destinatarios.")

def consultar_notificaciones():
    id_usuario = int(input("ID del usuario: "))
    cursor.execute("""
        SELECT un.Id, n.Titulo, n.Mensaje, un.FechaEnvio, un.Leida
        FROM UsuarioNotificacion un
        JOIN Notificaciones n ON n.Id = un.IdNotificacion
        WHERE un.IdUsuario = ?
        ORDER BY un.FechaEnvio DESC
    """, (id_usuario,))
    resultados = cursor.fetchall()
    if not resultados:
        print("🔕 No hay notificaciones.")
        return
    for notif in resultados:
        print(f"""
🔔 Notificación #{notif.Id}
Título: {notif.Titulo}
Mensaje: {notif.Mensaje}
Enviado: {notif.FechaEnvio}
Leído: {'Sí' if notif.Leida else 'No'}
        """)

def marcar_como_leida():
    id_usuario_notif = int(input("ID de la notificación a marcar como leída: "))
    cursor.execute("""
        UPDATE UsuarioNotificacion SET Leida = 1 WHERE Id = ?
    """, (id_usuario_notif,))
    conn.commit()
    print("✅ Notificación marcada como leída.")

# --- Menú interactivo ---
def menu():
    while True:
        print("""
===== SISTEMA DE NOTIFICACIONES =====
1. Agregar usuario
2. Crear y enviar notificación
3. Consultar notificaciones de un usuario
4. Marcar notificación como leída
5. Salir
""")
        opcion = input("Selecciona una opción: ")
        if opcion == '1':
            agregar_usuario()
        elif opcion == '2':
            crear_y_enviar_notificacion()
        elif opcion == '3':
            consultar_notificaciones()
        elif opcion == '4':
            marcar_como_leida()
        elif opcion == '5':
            print("👋 Cerrando sistema...")
            break
        else:
            print("❌ Opción no válida.")

# --- Iniciar menú ---
if __name__ == "__main__":
    try:
        menu()
    finally:
        conn.close()