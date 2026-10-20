# Operación local de RF-10

`stock_disponible` representa unidades físicas totales; `stock_reservado`, unidades
temporalmente comprometidas. Las unidades libres son su diferencia. El carrito no
reserva. Confirmar una orden reserva todas sus líneas y vacía el carrito dentro de
la misma transacción. Los detalles conservan nombre, vendedor, precio y cantidad.

La pantalla previa entrega una confirmación firmada, ligada a cuenta, selección y
precios. Tiene una validez de quince minutos para confirmar. La reserva tiene su
propio plazo de quince minutos desde la creación de la orden. Repetir la misma
confirmación devuelve la orden original, sin renovar reservas ni duplicar unidades.
Si cambian selección o precios se exige revisar un nuevo resumen.

## Vencimiento

Ejecutar desde `Codigo/`:

```powershell
.\.venv\Scripts\python.exe manage.py expirar_ordenes
```

El comando puede repetirse. También se intenta expirar al consultar órdenes y
antes de preparar o confirmar una nueva. No existe un servicio periódico configurado.
En un despliegue se debe programar el comando, por ejemplo mediante el Programador
de tareas de Windows. El vencimiento impide considerar vigente la reserva aunque
el mantenimiento todavía no haya actualizado estado y contadores; su liberación
persistida ocurre al ejecutar alguno de esos mecanismos. Sin mantenimiento, el
catálogo puede mostrar conservadoramente menos unidades libres.

## Integridad y límites

Las actualizaciones condicionales con `F()` adquieren unidades solo si hay stock
libre suficiente; una restricción impide reservar más unidades que las físicas.
La edición no puede reducir el físico bajo las reservas y el retiro exige cero
reservas. Las escrituras de la cabecera coordinan cambios de un mismo carrito.
SQLite puede rechazar una escritura concurrente por contención: se revierte toda
la operación y se informa el reintento. No se presupone bloqueo de filas mediante
`select_for_update()` en SQLite. MySQL requiere validación específica de su motor
e aislamiento antes del despliegue.

No hay pagos, pedidos ni reembolsos. RF-19 deberá revalidar de forma transaccional
estado pendiente, vencimiento futuro y reservas activas antes de admitir un pago;
una reserva expirada no debe reactivarse por una notificación tardía. La propiedad
`reserva_vigente` no sustituye esa futura operación transaccional de pago.

Referencias: [transacciones](https://docs.djangoproject.com/en/5.2/topics/db/transactions/),
[expresiones F](https://docs.djangoproject.com/en/5.2/ref/models/expressions/#avoiding-race-conditions-using-f),
[firma](https://docs.djangoproject.com/en/5.2/topics/signing/),
[bloqueos](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#select-for-update).

## RF-11: primera etapa del historial

`/ordenes/historial/` requiere una cuenta activa y mantiene separado el historial
de compras de «Mis órdenes». La consulta `compras_aprobadas_del_usuario` restringe
el propietario y devuelve deliberadamente `none()`: todavía no hay pagos aprobados
ni pedidos definitivos. Consultar el historial no expira órdenes ni altera reservas.

Quedan pendientes la integración verificable con RF-19 y la presentación de cada
compra con identificador, fecha efectiva de aprobación (no fecha de creación de la
orden), total histórico, número de pedidos, enlace al detalle y vendedores/estados
de sus pedidos. No debe sustituirse `none()` por todas las órdenes del comprador
ni usar las reservas como evidencia de pago. La selección de datos y las plantillas
de registros y detalle se completarán junto con esas dependencias. No se incorporan
estados, campos o relaciones ficticios en esta primera etapa.
