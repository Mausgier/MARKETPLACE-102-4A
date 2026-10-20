"""Formulario de alta que reúne datos de Producto y Publicacion."""

from decimal import Decimal

from django import forms

from .models import Categoria


class PublicacionForm(forms.Form):
    """
    Valida los datos públicos; excluye vendedor, producto existente y estado interno.

    https://docs.djangoproject.com/en/5.2/ref/forms/fields/#decimalfield
    https://docs.djangoproject.com/en/5.2/ref/forms/fields/#modelchoicefield
    """

    nombre = forms.CharField(label="Nombre del artículo", max_length=150)
    descripcion = forms.CharField(
        label="Descripción", max_length=5000,
        widget=forms.Textarea(attrs={"rows": 5}),
    )
    categoria = forms.ModelChoiceField(
        label="Categoría", queryset=Categoria.objects.all(),
        empty_label="Selecciona una categoría",
    )
    precio = forms.DecimalField(
        label="Precio", max_digits=12, decimal_places=2,
        min_value=Decimal("0.01"),
        help_text="Ingresa un monto mayor que cero, con hasta dos decimales.",
    )
    stock_disponible = forms.IntegerField(
        label="Cantidad inicial disponible", min_value=1, max_value=2147483647,
        help_text="Ingresa un número entero igual o superior a uno.",
    )

    def __init__(self, *args, **kwargs):
        """Mantiene la presentación Bootstrap utilizada por las cuentas."""
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            campo.widget.attrs["class"] = (
                "form-select" if isinstance(campo.widget, forms.Select)
                else "form-control"
            )
