"""Formularios públicos del catálogo, alta y edición de productos y publicaciones."""

from decimal import Decimal

from django import forms

from .models import Categoria


class BusquedaProductosForm(forms.Form):
    """
    Valida un término opcional; vacío recupera el catálogo sin búsqueda.

    https://docs.djangoproject.com/en/5.2/ref/forms/fields/#charfield
    """

    q = forms.CharField(
        label="Buscar productos", required=False, max_length=150, strip=True,
        help_text="Busca una palabra o frase en el nombre o la descripción (máximo 150 caracteres).",
        error_messages={
            "max_length": "El término de búsqueda no puede superar los 150 caracteres.",
        },
        widget=forms.TextInput(attrs={
            "type": "search", "class": "form-control",
        }),
    )


class CatalogoProductosForm(BusquedaProductosForm):
    """
    Integra búsqueda y filtros opcionales sin modificar las entidades comerciales.

    https://docs.djangoproject.com/en/5.2/ref/forms/fields/#modelchoicefield
    https://docs.djangoproject.com/en/5.2/ref/forms/fields/#decimalfield
    """

    categoria = forms.ModelChoiceField(
        label="Categoría", queryset=Categoria.objects.all(), required=False,
        empty_label="Todas las categorías",
        error_messages={"invalid_choice": "Selecciona una categoría existente."},
    )
    precio_minimo = forms.DecimalField(
        label="Precio mínimo", required=False, min_value=Decimal("0"),
        max_digits=12, decimal_places=2,
        help_text="Opcional. Desde este importe, incluido; hasta dos decimales.",
    )
    precio_maximo = forms.DecimalField(
        label="Precio máximo", required=False, min_value=Decimal("0"),
        max_digits=12, decimal_places=2,
        help_text="Opcional. Hasta este importe, incluido; hasta dos decimales.",
    )

    def __init__(self, *args, **kwargs):
        """Conserva la presentación de búsqueda y aplica Bootstrap a los filtros."""
        super().__init__(*args, **kwargs)
        for nombre in ("categoria", "precio_minimo", "precio_maximo"):
            self.fields[nombre].widget.attrs["class"] = (
                "form-select" if nombre == "categoria" else "form-control"
            )

    def clean(self):
        """
        Valida el rango completo sin impedir límites individuales o iguales.

        https://docs.djangoproject.com/en/5.2/ref/forms/validation/#cleaning-and-validating-fields-that-depend-on-each-other
        """
        datos = super().clean()
        minimo = datos.get("precio_minimo")
        maximo = datos.get("precio_maximo")
        if minimo is not None and maximo is not None and minimo > maximo:
            raise forms.ValidationError(
                "El precio mínimo no puede ser mayor que el precio máximo."
            )
        return datos


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


class EdicionPublicacionForm(PublicacionForm):
    """Reutiliza las validaciones del alta, permitiendo disponibilidad cero en RF-05."""

    stock_disponible = forms.IntegerField(
        label="Cantidad disponible", min_value=0, max_value=2147483647,
        help_text=("Ingresa un número entero igual o superior a cero. "
                   "Este cambio no modifica las unidades reservadas."),
    )

    def __init__(self, *args, publicacion, **kwargs):
        """Carga exclusivamente los campos editables de la publicación propia."""
        super().__init__(*args, **kwargs)
        self.initial.update({
            "nombre": publicacion.producto.nombre,
            "descripcion": publicacion.producto.descripcion,
            "categoria": publicacion.producto.categoria_id,
            "precio": publicacion.precio,
            "stock_disponible": publicacion.stock_disponible,
        })
