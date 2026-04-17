"""
Agregado raíz Incidencia.

Invariantes:
- Toda incidencia está asociada a un pedido.
- Un pedido entregado puede generar una incidencia (ej: reclamo).
- Una incidencia no puede cerrarse sin resolución.
- Al resolverse, puede gatillar acciones sobre el pedido.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import uuid
from .estados import EstadoIncidencia, Abierta


class TipoIncidencia(Enum):
    RECLAMO_NO_RECIBIDO = "reclamo_no_recibido"  # cliente dice que no recibió
    PRODUCTO_DAÑADO = "producto_dañado"
    INTENTO_FALLIDO = "intento_fallido"
    DIRECCION_INCORRECTA = "direccion_incorrecta"
    OTRO = "otro"


@dataclass
class Incidencia:
    id: str
    pedido_id: str
    tipo: TipoIncidencia
    descripcion: str
    resolucion_propuesta: str = ""
    accion_sobre_pedido: str = ""  # acción que gatilla sobre el pedido al resolverse
    _estado: EstadoIncidencia = field(default_factory=Abierta)

    @property
    def estado(self) -> str:
        return self._estado.nombre

    def analizar(self) -> None:
        self._estado.analizar(self)

    def pasar_a_resolucion(self, resolucion: str, accion: str = "") -> None:
        self._estado.resolver(self, resolucion)
        self.accion_sobre_pedido = accion

    def cerrar(self) -> None:
        self._estado.cerrar(self)


def generar_id_incidencia() -> str:
    return f"INC-{uuid.uuid4().hex[:8].upper()}"
