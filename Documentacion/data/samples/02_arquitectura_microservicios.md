# Patrones de Arquitectura de Microservicios y Contenedores en Nube

La transición de arquitecturas monolíticas hacia sistemas distribuidos basados en microservicios permite desacoplar los ciclos de vida de despliegue, aumentar la resiliencia y optimizar el escalado horizontal independiente.

## Principios Fundamentales
1. **Desacoplamiento de Datos:** Cada microservicio debe ser dueño de su propio almacén de datos (Database per Service) para evitar bloqueos y acoplamiento a nivel de esquema.
2. **Comunicación Asíncrona:** El uso de colas y buses de eventos (Kafka, RabbitMQ, OCI Streaming) amortigua picos de carga y previene fallos en cascada.
3. **API Gateways:** Centralizan la autenticación JWT, limitación de tasa (rate limiting), enrutamiento dinámico y terminación TLS.
4. **Observabilidad Distribuida:** Rastreo distribuido (Distributed Tracing con OpenTelemetry), métricas en tiempo real y agregación de logs estructurados.

## Consideraciones de Resiliencia
- Implementación de patrones Circuit Breaker (disyuntor) y Retry con jitter exponencial para evitar sobrecargar servicios degradados.
