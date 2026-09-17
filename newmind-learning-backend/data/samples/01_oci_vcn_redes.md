# Introducción a la Arquitectura de Redes Virtuales (VCN) en Oracle Cloud Infrastructure

La Virtual Cloud Network (VCN) es una red privada, personalizable y definida por software que se configura en los centros de datos de Oracle Cloud Infrastructure (OCI). Similar a una red de centro de datos tradicional en instalaciones físicas, la VCN ofrece control total sobre el entorno de red.

## Componentes Principales de una VCN
1. **Bloques CIDR:** Cada VCN cubre un único bloque contiguo de direcciones IPv4 privadas de su elección (por ejemplo, `10.0.0.0/16`).
2. **Subredes (Subnets):** Subdivisiones de la VCN que pueden ser públicas (las instancias reciben IPs públicas) o privadas (las instancias solo tienen IPs privadas y están aisladas del acceso público directo).
3. **Internet Gateway (IGW):** Enrutador de software opcional que proporciona una ruta para el tráfico directo de red hacia y desde Internet.
4. **NAT Gateway:** Permite que los recursos en una subred privada inicien conexiones salientes hacia Internet (para descargar parches o actualizaciones) sin exponerlos a conexiones entrantes no solicitadas.
5. **Route Tables (Tablas de Enrutamiento):** Reglas virtuales que dirigen el tráfico desde las subredes hacia destinos fuera de la VCN (como el Internet Gateway o redes on-premise).
6. **Security Lists (Listas de Seguridad):** Conjuntos de reglas de firewall virtuales a nivel de subred que controlan el tráfico entrante (ingress) y saliente (egress) por protocolo y puerto.

## Mejores Prácticas de Seguridad
- Implementar el principio de mínimo privilegio en las reglas de entrada.
- Alojar las bases de datos siempre en subredes privadas.
- Combinar Security Lists con Network Security Groups (NSGs) para granularidad a nivel de interfaz de red (VNIC).
