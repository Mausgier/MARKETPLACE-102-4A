from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager


class UsuarioManager(BaseUserManager):
    """
    Administra la creación de usuarios normales y administradores, utilizando el correo electrónico como identificador principal.
    https://docs.djangoproject.com/en/5.2/topics/auth/customizing/#writing-a-manager-for-a-custom-user-model

    """


    def create_user(self, email, password=None, **extra_fields):
        """
        Crea y almacena un usuario con su contraseña protegida.
        https://docs.djangoproject.com/en/5.2/topics/auth/customizing/#django.contrib.auth.models.CustomUserManager.create_user
        """

        # Comprueba que el correo no esté vacío ni contenga solo espacios.
        if (not email) or (not email.strip()):
            raise ValueError("El correo electrónico es obligatorio.")

        # Normaliza el dominio y convierte toda la dirección a minúsculas para mantener un formato uniforme durante el registro.
        email = self.normalize_email(email.strip()).lower()

        # Construye el usuario y protege su contraseña con el mecanismo de hash proporcionado por 'Django'.
        usuario = self.model(email=email, **extra_fields)
        usuario.set_password(password)
        usuario.save(using=self._db)

        return usuario


    def create_superuser(self, email, password=None, **extra_fields):
        """
        Crea y almacena un administrador con los permisos correspondientes.
        https://docs.djangoproject.com/en/5.2/topics/auth/customizing/#django.contrib.auth.models.CustomUserManager.create_superuser
        """

        # Establece los permisos necesarios para la administración.
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        # Impide crear administradores sin contraseña.
        if not password:
            raise ValueError("La contraseña es obligatoria.")

        # Comprueba que ambos permisos administrativos estén habilitados.
        if extra_fields.get("is_staff") is not True:
            raise ValueError("El administrador debe tener is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("El administrador debe tener is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractUser):
    """
    Representa las cuentas del marketplace y permite distinguir entre compradores y vendedores.
    """

    class Rol(models.TextChoices):
        """
        Define los roles comerciales disponibles en la plataforma.
        """

        COMPRADOR = "comprador", "Comprador"
        VENDEDOR = "vendedor", "Vendedor"

    # Elimina el nombre de usuario tradicional de 'Django'.
    username = None

    # Establece el correo electrónico como campo único.
    email = models.EmailField(
        verbose_name="Correo electrónico",
        unique=True
    )

    # Identifica el rol comercial de cada cuenta.
    rol = models.CharField(
        max_length=10,
        choices=Rol.choices,
        default=Rol.COMPRADOR
    )

    # Asocia el modelo con su administrador personalizado.
    objects = UsuarioManager()

    # Utiliza el correo electrónico para la autenticación.
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []


    def __str__(self):
        """
        Devuelve el correo electrónico que identifica al usuario.
        """

        return self.email
