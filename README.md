# Entregable 1 — DDD y Patrones de Diseño
## Logística de Última Milla

Proyecto que modela el dominio de una empresa de logística de última milla
aplicando **Domain-Driven Design**, **patrones de diseño** y **principios SOLID**.

---

## Cómo ejecutar

Requisitos: Python 3.10+ (solo biblioteca estándar, sin dependencias externas).

```bash
cd logistica
python main.py
```

La demo ejecuta los 4 casos de uso end-to-end:

1. **Gestión de Pedidos** — crear desde distintos canales, validar, gestionar estados.
2. **Gestión de Repartidores** — registrar, disponibilidad, asignación automática, re-asignación, ubicación.
3. **Monitoreo y Tracking** — visualizar estado, registrar eventos, notificar cliente.
4. **Gestión de Incidencias** — registrar reclamos, gestionar casos, resolver.

---

## Estructura del proyecto

```
logistica/
├── compartido/               # Published Language: eventos y bus de eventos
│   └── eventos.py
│
├── ventas/                   # Bounded Context: Ventas
│   ├── dominio/
│   │   ├── value_objects.py  # Dirección, Destinatario, Carga, …
│   │   ├── estados.py        # Patrón STATE del Pedido
│   │   ├── pedido.py         # Agregado raíz
│   │   └── factories.py      # FACTORY METHOD + ADAPTER por canal
│   ├── aplicacion/
│   │   └── servicio_pedidos.py
│   └── infraestructura/
│       └── repositorio.py    # REPOSITORY
│
├── operaciones/              # Bounded Context: Operaciones
│   ├── dominio/
│   │   ├── repartidor.py     # Agregado raíz
│   │   └── estrategias_asignacion.py  # Patrón STRATEGY
│   ├── aplicacion/
│   │   └── servicio_repartidores.py
│   └── infraestructura/
│       └── repositorio.py
│
├── tracking/                 # Bounded Context: Tracking (Conformist)
│   ├── dominio/
│   │   ├── seguimiento.py
│   │   └── canales_notificacion.py    # STRATEGY (canales)
│   ├── aplicacion/
│   │   └── servicio_tracking.py       # OBSERVER (se suscribe al bus)
│   └── infraestructura/
│       └── repositorio.py
│
├── incidencias/              # Bounded Context: Postventa / Incidencias
│   ├── dominio/
│   │   ├── estados.py        # STATE de la incidencia
│   │   └── incidencia.py
│   ├── aplicacion/
│   │   └── servicio_incidencias.py
│   └── infraestructura/
│       └── repositorio.py
│
└── main.py                   # Composition Root + demo
```

---

## Patrones aplicados

| Patrón | Tipo | Dónde |
|---|---|---|
| **Factory Method** | Creacional | `ventas/dominio/factories.py` — un factory por canal |
| **Adapter** | Estructural | Factories: traducen datos externos al modelo de dominio |
| **State** | Comportamiento | `ventas/dominio/estados.py` e `incidencias/dominio/estados.py` |
| **Strategy** | Comportamiento | `operaciones/dominio/estrategias_asignacion.py` + canales de notificación |
| **Observer** | Comportamiento | `compartido/eventos.py` (BusEventos) + `tracking/aplicacion` |
| **Repository** | DDD / Estructural | Todos los `infraestructura/repositorio.py` |

## SOLID aplicado

- **SRP**: cada clase tiene una sola responsabilidad (agregado, validador, servicio, repositorio, notificador).
- **OCP**: agregar un canal, una estrategia o un medio de notificación no modifica código existente.
- **LSP**: todos los `EstadoPedido` / `EstadoIncidencia` son intercambiables donde se espere la abstracción.
- **ISP**: interfaces de repositorio separadas por agregado (`IRepositorioPedidos`, `IRepositorioRepartidores`…).
- **DIP**: los servicios dependen de abstracciones; la inyección ocurre en `main.py` (Composition Root).
