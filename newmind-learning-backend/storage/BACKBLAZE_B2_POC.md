# Backblaze B2 POC (rama experimental)

Esta rama añade un proveedor opcional Backblaze B2 usando la API S3-compatible. OCI sigue siendo el proveedor predeterminado; no se reemplaza ni se elimina.

## Configuración

1. En Backblaze, habilitar B2 Cloud Storage y crear dos buckets privados.
2. Crear una Application Key con permisos mínimos sobre esos buckets (lectura/escritura de objetos según las operaciones que se vayan a probar). No usar la master application key.
3. Copiar el endpoint y región exactos mostrados por la consola.
4. En el `.env` del backend, configurar `STORAGE_PROVIDER=b2`, `B2_ENDPOINT_URL`, `B2_REGION`, `B2_KEY_ID`, `B2_APPLICATION_KEY`, `B2_BUCKET_DOCS` y `B2_BUCKET_OUTPUTS`.
5. Instalar dependencias con `pip install -r requirements.txt` y arrancar el backend.
6. Consultar `/health`. La respuesta conserva los campos públicos existentes:
   `oci_mode` y `oci_storage`. Cuando B2 está seleccionado, `oci_mode`
   debe ser `b2`, `oci_storage.provider` debe ser `backblaze_b2` y
   `oci_storage.mode` debe ser `b2` si el cliente se inicializó correctamente,
   o `local_emulation` si se está usando el fallback local.
7. Subir un documento de prueba, generar una adaptación y comprobar desde la consola B2 que ambos objetos existen. Para verificación real, descargar el objeto y comparar tamaño/hash; no basta con que la API responda 200.

## Fallback local

Si faltan credenciales o falla la inicialización o escritura, el cliente
puede guardar los objetos localmente y reportar `local_emulation`.
En ese caso, la respuesta no confirma persistencia en B2.

Consultar `oci_storage.error_code` en `/health` para identificar el
motivo reportado. La inicialización del cliente no demuestra por sí sola
que los buckets existan ni que las credenciales tengan permisos de escritura.

## Verificación de almacenamiento real

Esta prueba de concepto no se ha validado contra una cuenta B2 real.
Para verificarla, subir un documento de prueba y generar una adaptación;
comprobar ambos objetos en la consola B2 y descargar al menos uno para
comparar su contenido. No basta con que la API responda correctamente.

## Límites del POC

- La compatibilidad S3 cubre las operaciones usadas aquí (`PutObject`); no se han añadido todavía operaciones de lectura, borrado, URLs prefirmadas ni migración de objetos existentes de OCI.
- Los nombres de buckets deben existir previamente en la cuenta B2.
- No se incluyen credenciales en Git.
- Esta rama no se ha validado contra una cuenta B2 real en este entorno.

## Volver a OCI

Cambiar `STORAGE_PROVIDER=oci` y usar la configuración OCI actual. Si no se define `STORAGE_PROVIDER`, el valor predeterminado es `oci`.
