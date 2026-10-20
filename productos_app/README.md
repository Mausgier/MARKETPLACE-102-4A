# Administración de publicaciones — RF-15

La ruta `/articulos/administracion/` permite consultar publicaciones de todos los
vendedores, activas, retiradas o sin unidades libres. El acceso requiere cuenta
activa, `is_staff` y `productos_app.change_publicacion`. El permiso administrativo
de cuentas no concede este acceso. Un superusuario activo con acceso staff satisface
el permiso. Esta función no crea administradores ni asigna permisos.

Cada detalle privado se consulta en `/articulos/administracion/<id>/`, aunque ya no
sea visible en el catálogo público. Se presenta identificación, descripción,
categoría, vendedor, precio, unidades físicas, reservadas, libres y estado, sin
cargar contraseñas del vendedor. Las consultas no ejecutan mantenimiento de reservas.

El retiro utiliza POST con CSRF y redirección al detalle para confirmar el resultado.
Solo cambia el estado de la publicación elegida a `retirada`. El servicio comparte
con el retiro propio la condición de actualización: oferta activa, mismo vendedor
y cero unidades reservadas. La comprobación se realiza en la escritura para impedir
que un retiro invalide reservas adquiridas simultáneamente. Se conserva la fila y
sus relaciones; no se editan precios, propietarios, cantidades ni órdenes.

Si existen reservas, el retiro se bloquea. No hay liberación forzada ni cancelación
de órdenes. Las reservas vencidas que todavía figuren en el contador también
bloquean hasta que opere el mecanismo de expiración de RF-10. Esta interfaz no lo
ejecuta como efecto secundario. Tras el retiro, las condiciones de catálogo, carrito
y generación de órdenes impiden nuevas operaciones sobre la oferta.

Las rutas de vendedores siguen restringidas por propietario, incluso para cuentas
administrativas. La supervisión no concede edición ajena ni reactivación de ofertas.
No se incorporan entidades o migraciones nuevas. La revisión visual y las pruebas
formales posteriores deben completarse por separado de las comprobaciones técnicas.

Referencias: [permisos](https://docs.djangoproject.com/en/5.2/topics/auth/default/#permissions-and-authorization),
[actualización condicional](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#update),
[transacciones](https://docs.djangoproject.com/en/5.2/topics/db/transactions/).
