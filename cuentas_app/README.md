# Administración de usuarios — RF-14

La ruta `/cuentas/administracion/usuarios/` muestra cuentas paginadas con nombre,
apellido, correo, identificador y estado. El listado no carga ni presenta hashes de
contraseña. Las operaciones cambian únicamente `is_active`; no modifican permisos,
contraseñas o información comercial.

El acceso exige autenticación, cuenta activa, `is_staff` y el permiso
`cuentas_app.change_usuario`. Un superusuario activo con acceso staff satisface el
permiso. La preferencia comprador/vendedor no interviene. Esta función no asigna
permisos ni crea administradores. Los permisos existentes de Django no necesitan
migraciones adicionales.

Suspensión y reactivación requieren POST con CSRF. La suspensión de cualquier cuenta
con `is_staff` o `is_superuser` está prohibida, incluso con varios administradores;
esta política conservadora evita suspender la propia cuenta o dejar el sistema sin
acceso administrativo mediante esta interfaz. No existe borrado de usuarios.

La suspensión invalida las sesiones vigentes de la cuenta en el motor actual,
`django.contrib.sessions.backends.db`, dentro de la misma transacción que el cambio
de estado. La reactivación no restaura esas sesiones y exige nueva autenticación.
La revocación recorre sesiones vigentes porque Django no dispone de una relación
directa sesión-usuario. Si se cambia el motor, debe adaptarse este mecanismo.
No se garantiza detener solicitudes que ya se estaban ejecutando al suspender.

Las publicaciones existentes continúan sujetas a sus reglas actuales de visibilidad;
las órdenes y reservas no se cancelan ni liberan por suspender al usuario. RF-14 no
añade una política comercial de retirada o cancelación por suspensión.

Comprobaciones desde `Codigo/`:

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
```

Referencias: [permisos](https://docs.djangoproject.com/en/5.2/topics/auth/default/#permissions-and-authorization),
[sesiones fuera de vistas](https://docs.djangoproject.com/en/5.2/topics/http/sessions/#using-sessions-out-of-views).
