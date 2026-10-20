"""Validación compartida de cantidades al incorporar y modificar artículos."""

from django import forms


class CantidadCarritoForm(forms.Form):
    """Acepta solo enteros positivos; el servicio valida su relación con el stock."""

    cantidad = forms.IntegerField(
        label="Cantidad", min_value=1, max_value=2147483647,
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "1"}),
        error_messages={"invalid": "Ingresa una cantidad entera válida."},
    )
