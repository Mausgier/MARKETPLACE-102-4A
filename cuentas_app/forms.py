from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Usuario


class RegistroUsuarioForm(UserCreationForm):
    """
    Gestiona los datos y las validaciones necesarias para registrar compradores y vendedores.
    https://docs.djangoproject.com/en/5.2/topics/auth/default/#django.contrib.auth.forms.UserCreationForm
    """

    MENSAJE_CORREO_DUPLICADO = "Este correo electrónico ya está registrado."

    # Solicita el nombre como campo obligatorio.
    first_name = forms.CharField(
        label="Nombre",
        max_length=150,
        required=True
    )

    # Solicita el apellido como campo obligatorio.
    last_name = forms.CharField(
        label="Apellido",
        max_length=150,
        required=True
    )

    class Meta:
        """
        Define el modelo y los campos utilizados en el formulario público de registro.
        """

        model = Usuario
        fields = (
            "first_name",
            "last_name",
            "email",
            "rol",
        )

    def __init__(self, *args, **kwargs):
        """
        Configura las etiquetas, ayudas y presentación del formulario de registro.

        https://docs.djangoproject.com/en/5.2/ref/forms/widgets/#styling-widget-instances
        """
        super().__init__(*args, **kwargs)

        # RN-01: esta preferencia no concede ni restringe capacidades comerciales.
        self.fields["rol"].label = "Preferencia comercial inicial"
        self.fields["rol"].help_text = (
            "Puedes comprar y vender con la misma cuenta, "
            "independientemente de esta preferencia."
        )
        self.fields["password1"].label = "Contraseña"
        self.fields["password2"].label = "Confirmar contraseña"
        self.fields["password2"].help_text = (
            "Repite la contraseña para comprobar que está escrita correctamente."
        )

        autocompletado = {
            "first_name": "given-name",
            "last_name": "family-name",
            "email": "email",
            "password1": "new-password",
            "password2": "new-password",
        }
        for nombre, campo in self.fields.items():
            campo.widget.attrs["class"] = (
                "form-select" if isinstance(campo.widget, forms.Select)
                else "form-control"
            )
            if nombre in autocompletado:
                campo.widget.attrs["autocomplete"] = autocompletado[nombre]

    def clean_email(self):
        """
        Normaliza el correo electrónico y comprueba que no exista otra cuenta con la misma dirección.
        """

        # Obtiene el correo validado por el campo 'EmailField'.
        email = self.cleaned_data["email"].strip().lower()

        # Impide registrar correos existentes, incluso cuando contienen diferencias entre mayúsculas y minúsculas.
        if Usuario.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                self.MENSAJE_CORREO_DUPLICADO,
                code="correo_duplicado",
            )

        return email
