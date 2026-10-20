# Marketplace — Ingeniería de Software (Evaluación Sumativa N.° 3)

Prototipo académico de una plataforma web de compra y venta de artículos, desarrollado con **Python y Django** para la asignatura **Ingeniería de Software, sección 102-4A**.

El proyecto permite explorar publicaciones y gestionar operaciones de compradores, vendedores y administradores. Su desarrollo es **incremental**: algunas funcionalidades están implementadas y otras permanecen parciales o pendientes. **No está preparado para un entorno productivo ni realiza cobros reales.**

## Tecnologías

- **Python 3.14** (versión utilizada para fijar el entorno de desarrollo).
- **Django 5.2.18** (rama 5.2 LTS).
- **SQLite** como base de datos local de desarrollo.
- **python-dotenv 1.2.4** para cargar la configuración desde un archivo `.env` privado.
- Plantillas HTML y hojas de estilo para la interfaz web.

La utilización de **MySQL** y una infraestructura en la nube forma parte de la propuesta arquitectónica, **no** de la configuración ejecutable que contiene actualmente el repositorio.

## Requisitos previos

1. Tener **Python 3.14** instalado y disponible desde la terminal.
2. Tener **Git** instalado si se desea clonar el repositorio.
3. Disponer de una terminal (los pasos principales están escritos para **Windows PowerShell**).
4. Tener acceso a internet durante la instalación de dependencias.

> Todos los comandos deben ejecutarse desde la **raíz del repositorio**, donde se encuentran `manage.py`, `requirements.txt` y `config/`. En el directorio original de desarrollo, esa ubicación corresponde a `Codigo/`.

## Instalación y ejecución — Windows PowerShell

### 1. Obtener el proyecto

```powershell
git clone https://github.com/Mausgier/MARKETPLACE-102-4A.git
cd MARKETPLACE-102-4A
```

Si ya tienes el código descargado o clonado, simplemente abre una terminal en el directorio que contiene `manage.py`.

### 2. Crear un entorno virtual e instalar dependencias

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Se utiliza el ejecutable del entorno virtual directamente, por lo que **no es necesario cambiar la política de ejecución de PowerShell** para activar scripts.

### 3. Configurar la clave secreta local

```powershell
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -c "from pathlib import Path; import secrets; Path('.env').write_text('DJANGO_SECRET_KEY=' + secrets.token_urlsafe(50) + '\n', encoding='utf-8')"
```

Estos comandos crean el archivo `.env` y generan una clave aleatoria para el entorno local. **No compartas ni subas el contenido de `.env`**: está excluido del repositorio mediante `.gitignore`.

Si ya tienes un `.env` con una clave propia, **no repitas este paso**, porque el segundo comando lo reemplaza.

### 4. Crear la base de datos y aplicar migraciones

```powershell
.\.venv\Scripts\python.exe manage.py migrate
```

Esto crea la base SQLite local `db.sqlite3`, aplica las migraciones existentes e incorpora las categorías iniciales definidas en las migraciones del proyecto. La base de datos y los usuarios de otra instalación **no** vienen incluidos en Git.

### 5. Iniciar el servidor de desarrollo

```powershell
.\.venv\Scripts\python.exe manage.py runserver
```

Abre estas direcciones en el navegador:

| Dirección | Función |
| --- | --- |
| <http://127.0.0.1:8000/> | Entrada al sitio (redirección al módulo de cuentas) |
| <http://127.0.0.1:8000/cuentas/registro/> | Crear una cuenta |
| <http://127.0.0.1:8000/cuentas/iniciar-sesion/> | Iniciar sesión |
| <http://127.0.0.1:8000/articulos/> | Catálogo público |
| <http://127.0.0.1:8000/carrito/> | Carrito del usuario autenticado |
| <http://127.0.0.1:8000/ordenes/> | Consulta de órdenes propias |
| <http://127.0.0.1:8000/admin/> | Panel de administración de Django |

Para detener el servidor, presiona **Ctrl + C** en la terminal.

### 6. Crear una cuenta administrativa (opcional)

Después de aplicar las migraciones, ejecuta en otra terminal:

```powershell
.\.venv\Scripts\python.exe manage.py createsuperuser
```

El modelo de usuario utiliza el **correo electrónico** como identificador principal. Sigue las instrucciones de la terminal para definirlo y establecer una contraseña. La cuenta permite acceder al panel `/admin/` y a las funcionalidades administrativas autorizadas.

### Primer uso

1. Registra una cuenta desde la interfaz web e inicia sesión.
2. Crea una publicación desde **Publicar**; el catálogo inicialmente estará vacío hasta que se registren publicaciones.
3. Consulta las publicaciones en **Artículos**, utiliza la búsqueda y los filtros, o agrega artículos al carrito.
4. Desde **Mi carrito**, revisa los artículos para generar una orden con reserva temporal.

La preferencia inicial de comprador o vendedor no impide realizar ambas actividades con la misma cuenta. No es necesario cargar datos personales reales para evaluar el prototipo.

## Ejecución en macOS o Linux

Desde la raíz del repositorio, si está disponible `python3.14`:

```bash
python3.14 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
./.venv/bin/python -c "from pathlib import Path; import secrets; Path('.env').write_text('DJANGO_SECRET_KEY=' + secrets.token_urlsafe(50) + '\n', encoding='utf-8')"
./.venv/bin/python manage.py migrate
./.venv/bin/python manage.py runserver
```

No repitas la creación del `.env` si ya existe uno con una clave válida. Las instrucciones de este apartado son equivalentes a las de Windows, pero no sustituyen una validación específica en cada plataforma.

## Organización del repositorio

```text
MARKETPLACE-102-4A/
├── config/          # Configuración general y rutas principales de Django
├── cuentas_app/     # Registro, sesiones, perfiles y administración de usuarios
├── productos_app/   # Productos, publicaciones, catálogo, búsqueda y filtros
├── carrito_app/     # Carrito y cantidades seleccionadas
├── ordenes_app/     # Órdenes, reservas temporales y consultas de historial/ventas
├── pagos_app/       # Base técnica de intentos de pago, sin pasarela conectada
├── manage.py        # Utilidad de administración de Django
├── requirements.txt # Dependencias con versiones fijadas
├── .env.example     # Plantilla de configuración local, sin credenciales
└── .gitignore       # Exclusiones de secretos y archivos generados
```

> Esta estructura describe los archivos comprobados en la rama `main` al redactar este README. Si se publican incrementos posteriores (por ejemplo, un módulo de pedidos o consolidación comercial de pagos), esta sección y el estado funcional deberán actualizarse para representar el código efectivamente disponible.

## Funcionalidades y alcance actual

En el código publicado se encuentran implementados los componentes principales para:

- Registro de cuentas, autenticación por correo electrónico, cierre de sesión y modificación del perfil.
- Creación, edición y retiro lógico de publicaciones del vendedor.
- Listado público de artículos, búsqueda, filtros por categoría y precio, paginación y detalle.
- Carrito de compras: agregar, modificar cantidades, eliminar artículos y consultar importes estimados.
- Generación de órdenes con **reservas de existencias por 15 minutos**, validaciones de disponibilidad y liberación de reservas vencidas.
- Consultas preparatorias de **historial de compras** y **mis ventas**. No representan pagos aprobados mientras no exista la integración comercial correspondiente.
- Supervisión de cuentas y publicaciones mediante permisos administrativos específicos.
- Registro interno de **intentos de pago**, referencias e idempotencia como base para una integración futura.

**Limitaciones:** no se ha conectado una pasarela financiera externa; no se realizan cargos reales ni reembolsos. El historial de compras pagadas y las ventas efectivas requieren completar sus dependencias financieras. Tampoco se ha efectuado un despliegue productivo de MySQL o de infraestructura IaaS.

## Órdenes y expiración de reservas

El carrito **no reserva existencias**. Al confirmar una orden se comprometen temporalmente las unidades correspondientes, con una vigencia de **15 minutos**.

En la rama publicada existe el comando de mantenimiento:

```powershell
.\.venv\Scripts\python.exe manage.py expirar_ordenes
```

Puede ejecutarse varias veces sin duplicar liberaciones. Algunas consultas y operaciones de órdenes también intentan procesar vencimientos. **No existe un programador periódico configurado**, por lo que para una ejecución permanente se necesitaría planificar este comando externamente. Las reservas vencidas no deben considerarse vigentes aunque todavía no se haya ejecutado su actualización persistente.

## Comprobaciones de desarrollo

Desde la raíz del repositorio, en PowerShell:

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe manage.py migrate --check
.\.venv\Scripts\python.exe manage.py test
```

Estos comandos revisan la configuración, comprueban el estado de las migraciones y ejecutan los tests disponibles en la versión descargada. **No equivalen a una certificación de seguridad ni a una campaña completa de testing**. Django utiliza una base de datos de pruebas aislada durante sus pruebas automatizadas.

## Seguridad y consideraciones de despliegue

- La configuración requiere una `DJANGO_SECRET_KEY` privada y no la incluye en el código fuente.
- `.env`, bases SQLite locales, entornos virtuales y archivos sensibles están excluidos mediante `.gitignore`.
- El servidor iniciado con `runserver` es **solo para desarrollo**.
- En la configuración disponible, `DEBUG=True` y `ALLOWED_HOSTS=[]`, adecuados únicamente para ejecución local; no desplegar así en internet.
- La migración a **MySQL** y el uso de infraestructura **IaaS** son propuestas de evolución, no configuraciones verificadas en este repositorio.
- No se deben introducir números de tarjeta, CVV, tokens de proveedores financieros ni credenciales reales en el prototipo.

## Documentación y referencias

- [Documentación oficial de Django 5.2](https://docs.djangoproject.com/en/5.2/)
- [Instalación de Django](https://docs.djangoproject.com/en/5.2/topics/install/)
- [Migraciones de bases de datos](https://docs.djangoproject.com/en/5.2/topics/migrations/)
- [Administración de usuarios y autenticación](https://docs.djangoproject.com/en/5.2/topics/auth/)
- [Lista de verificación para un despliegue seguro](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)

Este repositorio es un **proyecto académico en desarrollo** y se proporciona para revisión y ejecución local del prototipo.
