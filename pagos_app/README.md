# RF-19.1 — Base de intentos de pago

Esta aplicación representa intentos y define un contrato abstracto de proveedor.
No tiene rutas, botones, registro editable en Django Admin, adaptador concreto,
cliente HTTP ni credenciales. No efectúa cobros reales o sandbox, no aprueba pagos,
no marca órdenes pagadas, no consume inventario y no crea pedidos ni reembolsos.

## Entidad y responsabilidades

`IntentoPago` pertenece a una `OrdenCompra` protegida contra eliminación. Conserva
UUID propio, clave de idempotencia, referencia comercial aleatoria única,
proveedor, ambiente, monto, moneda, estado, estado de verificación y fechas.
La referencia externa es opcional y única por proveedor y ambiente cuando existe.
Proveedor vacío significa que todavía no se seleccionó uno. El ambiente por defecto
es pruebas; las opciones del modelo no configuran ni habilitan esos ambientes.

El resultado financiero conserva Pendiente, Aprobado, Rechazado y Cancelado.
La verificación distingue Sin verificar, Requiere consulta externa y Resultado
verificado. Un error de comunicación no debe transformarse en un rechazo: permanece
Pendiente y requiere consulta. Un resultado terminal exige estructuralmente fecha
de verificación, proveedor y referencia externa. Esos metadatos no acreditan por sí
solos autenticidad: el futuro adaptador deberá verificar la pasarela directamente.
En RF-19.1 no existe operación para registrar aprobaciones, ni simuladas ni manuales.

## Importes CLP y datos anteriores

Los intentos utilizan `Decimal` con cero decimales y monto positivo. Antes del
guardado ordinario se valida que el importe ya sea entero, finito y exactamente
igual al total histórico de la orden. Nunca se cuantiza un importe fraccionario
para convertirlo en entero. Se rechazan entradas float y booleanas.

El límite del intento es 999999999999999 CLP (quince dígitos), explícito y conservador
para el almacenamiento local en SQLite. Los importes superiores se rechazan. La
restricción de base de datos también exige monto entero y dentro del límite.
La igualdad entre tablas se valida en el modelo/servicio, no mediante una restricción
SQL entre tablas. `QuerySet.update()` y operaciones masivas omiten la validación
del modelo y no deben utilizarse para cambiar importes o asociar otro pago.

Los modelos, precios y órdenes anteriores no se convierten ni se redondean. Una
orden con total 100.50 se conserva exactamente, pero no admite un intento CLP.
Una orden con total 100.00 admite un intento por 100 CLP. No hay migración de datos
ni cambios en los formularios del catálogo como parte de este incremento.

## Registro técnico interno e idempotencia

`registrar_intento_pendiente` es un servicio interno sin exposición HTTP. Requiere
cuenta activa, orden propia pendiente y plazo vigente para un registro nuevo.
Obtiene el monto desde la orden, nunca del navegador. Solo escribe en la tabla de
intentos; no expira órdenes ni altera reservas. La clave debe proceder del servidor
cuando se incorpore la interfaz futura, y es independiente de la firma de RF-10.

Repetir la clave devuelve el mismo registro; reutilizarla con otra orden, proveedor
o ambiente se rechaza. Una repetición de un registro ya existente fuera del plazo
solo recupera sus metadatos: no inicia una transacción ni extiende su reserva.
Claves diferentes permiten varios intentos por orden. En esta etapa no se implementa
la exclusión operativa de varios cobros externos en curso porque no hay cobros.

SQLite incorpora un índice único condicional para impedir dos filas Aprobado por
orden. Ese índice no acredita confirmaciones externas ni aplica comercialmente un
pago. MySQL no admite esa misma restricción condicional: antes de usarlo deberá
incorporarse una garantía portable. RF-19.2 debe implementar la aplicación comercial
única, sus transiciones atómicas y la coordinación con expiración e inventario.

## Contrato de proveedor y siguientes incrementos

`ProveedorPago` es abstracto: define iniciar y consultar, con estructuras mínimas
de solicitud/respuesta. Una implementación futura deberá autenticar HTTPS y
comprobar comercio, ambiente, referencias, monto y moneda. Una respuesta recibida
desde el navegador o la mera construcción de un objeto `ResultadoVerificado`
nunca bastarán para aprobar. Flow solo es una alternativa por evaluar.

Permanecen pendientes la integración externa, conciliación de cobros no aplicables,
registros de incidencias financieras, pedidos, pagos aplicados y reembolsos.
Se conserva el vencimiento de quince minutos desde la creación de la orden.
Una aprobación externa tardía no deberá reactivar reservas ni generar pedidos
automáticamente; su registro y conciliación se completarán en el incremento correspondiente.

No se deben almacenar números de tarjeta, CVV, claves privadas, tokens de acceso
ni respuestas completas de la pasarela. `referencia_externa` identifica una
transacción; no es un campo para credenciales.

Referencias: [restricciones](https://docs.djangoproject.com/en/5.2/ref/models/constraints/),
[validación](https://docs.djangoproject.com/en/5.2/ref/models/instances/#validating-objects),
[get_or_create](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#get-or-create).
