"""Entrada de confirmación sin aceptar importes o propietarios del navegador."""

from django import forms


class ConfirmarOrdenForm(forms.Form):
    """Recibe exclusivamente el resumen firmado generado por el servidor."""

    token = forms.CharField(max_length=2048, widget=forms.HiddenInput)
